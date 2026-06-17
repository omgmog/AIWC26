# Pre-computes the leaderboard, per-fixture scoring and the "next match"
# widget at build time, so the templates only need to do markup.
require "json"

module AIWC26
  class ScoringGenerator < Jekyll::Generator
    safe true
    priority :high

    def generate(site)
      data = site.data
      teams = data["fixtures"]["teams"]
      fixtures = data["fixtures"]["fixtures"]
      results = data["results"]["results"] || {}
      manifest = data["manifest"]["predictions"]
      predictions_dir = File.join(site.source, "_data", "predictions")

      validate_actual_home!(fixtures)

      # Read prediction files directly by filename: Jekyll's _data loader
      # strips dots from keys (e.g. "gemini-1.5-pro.json" -> "gemini-15-pro"),
      # which would no longer match manifest.json's filenames.
      models = manifest.map do |filename|
        entry = JSON.parse(File.read(File.join(predictions_dir, filename)))
        by_fixture = {}
        entry["predictions"].each { |p| by_fixture[p["fixture_id"]] = p }
        {
          "model" => entry["model"],
          "provider" => entry["provider"],
          "generated" => entry["generated"],
          "method_notes" => entry["method_notes"],
          "by_fixture" => by_fixture,
        }
      end

      fixtures_grouped, fixtures_by_date = fixture_rows(models, fixtures, teams, results)

      site.data["computed"] = {
        "models" => models,
        "leaderboard" => leaderboard(models, fixtures, results),
        "groups" => fixtures.map { |f| f["group"] }.uniq,
        "fixtures" => fixtures_grouped,
        "fixtures_by_date" => fixtures_by_date,
        "next_match" => next_match(fixtures, teams, results, site.time),
      }
    end

    private

    def validate_actual_home!(fixtures)
      fixtures.each do |f|
        actual_home = f["actual_home"]
        next unless actual_home
        next if [f["home"], f["away"]].include?(actual_home)

        raise "fixture #{f['id']}: actual_home #{actual_home.inspect} is not " \
              "#{f['home']} or #{f['away']}"
      end
    end

    def outcome(home, away)
      home > away ? "H" : home < away ? "A" : "D"
    end

    # Flips a "h-a" score string to "a-h" for transposed display; leaves
    # non-score placeholders (e.g. "—") untouched.
    def flip_score(text)
      m = text.match(/\A(\d+)-(\d+)\z/)
      m ? "#{m[2]}-#{m[1]}" : text
    end

    # Mirrors scoreCell() from the original client-side renderer.
    def score_cell(pred, res)
      return { "cls" => "noft", "text" => "—", "pts" => nil } unless pred

      text = "#{pred['home_score']}-#{pred['away_score']}"
      return { "cls" => "p-pending", "text" => text, "pts" => nil } unless res

      if pred["home_score"] == res["home_score"] && pred["away_score"] == res["away_score"]
        { "cls" => "p-exact", "text" => text, "pts" => 3 }
      elsif outcome(pred["home_score"], pred["away_score"]) == outcome(res["home_score"], res["away_score"])
        { "cls" => "p-result", "text" => text, "pts" => 1 }
      else
        { "cls" => "p-wrong", "text" => text, "pts" => 0 }
      end
    end

    def leaderboard(models, fixtures, results)
      tally = models.map { |m| { "model" => m, "scored" => 0, "exact" => 0, "result" => 0, "pts" => 0 } }

      fixtures.each do |f|
        res = results[f["id"]]
        next unless res

        tally.each do |t|
          cell = score_cell(t["model"]["by_fixture"][f["id"]], res)
          next if cell["pts"].nil?

          t["scored"] += 1
          case cell["pts"]
          when 3 then t["exact"] += 1; t["pts"] += 3
          when 1 then t["result"] += 1; t["pts"] += 1
          end
        end
      end

      tally.sort_by! { |t| [-t["pts"], -t["exact"]] }
      tally.each_with_index { |t, i| t["crown"] = i.zero? && t["pts"] > 0 }
      tally
    end

    def fixture_rows(models, fixtures, teams, results)
      rows_by_id = fixtures.to_h { |f| [f["id"], fixture_row(f, models, teams, results)] }

      grouped = fixtures
        .group_by { |f| f["group"] }
        .flat_map { |_, group_fixtures| sort_fixtures(group_fixtures, results) }
        .map { |f| rows_by_id[f["id"]] }

      by_date = fixtures
        .sort_by { |f| [f["date"].to_s, f["time"].to_s, f["id"]] }
        .map { |f| rows_by_id[f["id"]] }

      [grouped, by_date]
    end

    def sort_fixtures(fixtures, results)
      fixtures.sort_by { |f| [results[f["id"]] ? 0 : 1, f["date"].to_s, f["time"].to_s, f["id"]] }
    end

    def fixture_row(f, models, teams, results)
      res = results[f["id"]]
      transposed = f["actual_home"] && f["actual_home"] != f["home"]

      cells = models.map do |m|
        pred = m["by_fixture"][f["id"]]
        cell = score_cell(pred, res)
        cell = cell.merge("text" => flip_score(cell["text"])) if transposed
        cell.merge("reasoning" => pred ? (pred["reasoning"] || "") : "")
      end

      outcomes = models.filter_map do |m|
        pred = m["by_fixture"][f["id"]]
        pred && outcome(pred["home_score"], pred["away_score"])
      end.uniq

      if res
        score_text = transposed ? "#{res['away_score']}-#{res['home_score']}" : "#{res['home_score']}-#{res['away_score']}"
        ft_text = "#{score_text} FT"
      else
        ft_text = f["date"] || "v"
      end
      ft_class = res ? "ft" : "noft"

      home_code, away_code = transposed ? [f["away"], f["home"]] : [f["home"], f["away"]]

      {
        "id" => f["id"],
        "group" => f["group"],
        "date" => f["date"],
        "time" => f["time"],
        "home_code" => home_code,
        "away_code" => away_code,
        "home_name" => teams[home_code]["name"],
        "away_name" => teams[away_code]["name"],
        "venue" => f["venue"],
        "ft_text" => ft_text,
        "ft_class" => ft_class,
        "disagree" => outcomes.length > 1,
        "cells" => cells,
      }
    end

    def next_match(fixtures, teams, results, build_time)
      today = build_time.strftime("%Y-%m-%d")
      pending = fixtures.select { |f| f["date"] && !results[f["id"]] }.sort_by { |f| f["date"] }
      return nil if pending.empty?

      f = pending.first
      when_label = f["date"] == today ? "TODAY" : f["date"] < today ? "OVERDUE" : f["date"]
      transposed = f["actual_home"] && f["actual_home"] != f["home"]
      home_code, away_code = transposed ? [f["away"], f["home"]] : [f["home"], f["away"]]

      {
        "group" => f["group"],
        "when" => when_label,
        "home_name" => teams[home_code]["name"],
        "away_name" => teams[away_code]["name"],
        "venue" => f["venue"],
      }
    end
  end
end
