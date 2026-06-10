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

      site.data["computed"] = {
        "models" => models,
        "leaderboard" => leaderboard(models, fixtures, results),
        "groups" => fixtures.map { |f| f["group"] }.uniq,
        "fixtures" => fixture_rows(models, fixtures, teams, results),
        "next_match" => next_match(fixtures, teams, results, site.time),
      }
    end

    private

    def outcome(home, away)
      home > away ? "H" : home < away ? "A" : "D"
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
      fixtures.map do |f|
        res = results[f["id"]]

        cells = models.map do |m|
          pred = m["by_fixture"][f["id"]]
          cell = score_cell(pred, res)
          cell.merge("reasoning" => pred ? (pred["reasoning"] || "") : "")
        end

        outcomes = models.filter_map do |m|
          pred = m["by_fixture"][f["id"]]
          pred && outcome(pred["home_score"], pred["away_score"])
        end.uniq

        ft_text = res ? "#{res['home_score']}-#{res['away_score']} FT" : (f["date"] || "v")
        ft_class = res ? "ft" : "noft"

        {
          "id" => f["id"],
          "group" => f["group"],
          "home_code" => f["home"],
          "away_code" => f["away"],
          "home_name" => teams[f["home"]]["name"],
          "away_name" => teams[f["away"]]["name"],
          "ft_text" => ft_text,
          "ft_class" => ft_class,
          "disagree" => outcomes.length > 1,
          "cells" => cells,
        }
      end
    end

    def next_match(fixtures, teams, results, build_time)
      today = build_time.strftime("%Y-%m-%d")
      pending = fixtures.select { |f| f["date"] && !results[f["id"]] }.sort_by { |f| f["date"] }
      return nil if pending.empty?

      f = pending.first
      when_label = f["date"] == today ? "TODAY" : f["date"] < today ? "OVERDUE" : f["date"]

      {
        "group" => f["group"],
        "when" => when_label,
        "home_name" => teams[f["home"]]["name"],
        "away_name" => teams[f["away"]]["name"],
      }
    end
  end
end
