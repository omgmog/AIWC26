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
      stage_defs = data["fixtures"]["stages"]

      validate_actual_home!(fixtures)
      validate_knockout_winners!(fixtures, results)

      # Read prediction files directly by filename: Jekyll's _data loader
      # strips dots from keys (e.g. "gemini-1.5-pro.json" -> "gemini-15-pro"),
      # which would no longer match manifest.json's filenames. The group
      # stage's predictions live at the top level (_data/predictions/<file>);
      # every later stage's predictions live in their own subfolder
      # (_data/predictions/<stage>/<file>) since each round is a fresh,
      # immutable prompt sent after the previous round's results are known.
      # The root file is optional: a model that joins mid-tournament (e.g.
      # replacing one that's no longer available) may only have stage files.
      models = manifest.map do |filename|
        paths = [File.join(predictions_dir, filename)]
        stage_defs.each do |stage_def|
          next if stage_def["key"] == "group"
          paths << File.join(predictions_dir, stage_def["key"], filename)
        end
        entries = paths.select { |p| File.exist?(p) }.map { |p| JSON.parse(File.read(p)) }
        raise "no prediction files found for #{filename}" if entries.empty?

        by_fixture = {}
        entries.each { |e| e["predictions"].each { |p| by_fixture[p["fixture_id"]] = p } }
        meta = entries.first

        {
          "model" => meta["model"],
          "provider" => meta["provider"],
          "generated" => meta["generated"],
          "method_notes" => meta["method_notes"],
          "by_fixture" => by_fixture,
        }
      end

      fixtures_by_stage = fixtures.group_by { |f| f["stage"] }

      seen_fixtures = []
      stages = {}
      current_stage = nil

      stage_defs.each do |stage_def|
        key = stage_def["key"]
        stage_fixtures = fixtures_by_stage[key] || []
        next if stage_fixtures.empty?

        seen_fixtures += stage_fixtures

        # Drop models with no predictions at all for this stage (e.g. a
        # model retired between rounds) so they don't show an all-dashes
        # column or sit frozen at 0pts looking like they predicted every
        # fixture wrong.
        stage_models = models.select { |m| stage_fixtures.any? { |f| m["by_fixture"].key?(f["id"]) } }

        grouped, by_date = fixture_rows(stage_models, stage_fixtures, teams, results)

        stages[key] = {
          "key" => key,
          "label" => stage_def["label"],
          "groups" => stage_fixtures.map { |f| f["group"] }.uniq,
          "models" => stage_models,
          "fixtures" => grouped,
          "fixtures_by_date" => by_date,
          "leaderboard" => leaderboard(stage_models, stage_fixtures, results),
          "leaderboard_through" => leaderboard(stage_models, seen_fixtures, results),
        }

        pending = stage_fixtures.any? { |f| !results[f["id"]] }
        current_stage ||= key if pending
      end
      current_stage ||= stages.keys.last

      site.data["computed"] = {
        "models" => models,
        "current_stage" => current_stage,
        "stages" => stages,
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

    # Knockout fixtures can't end level: a draw after 90 minutes goes to
    # extra time, then penalties. results.json records the 90-minute score
    # plus an explicit "winner" (who actually went through), since that
    # can't always be derived from the scoreline alone.
    def validate_knockout_winners!(fixtures, results)
      fixtures.each do |f|
        next if f["stage"] == "group"
        res = results[f["id"]]
        next unless res

        winner = res["winner"]
        next if [f["home"], f["away"]].include?(winner)

        raise "fixture #{f['id']}: knockout result needs a \"winner\" matching " \
              "#{f['home']} or #{f['away']}, got #{winner.inspect}"
      end
    end

    # Flips a "h-a" score string to "a-h" for transposed display; leaves
    # non-score placeholders (e.g. "—") untouched.
    def flip_score(text)
      m = text.match(/\A(\d+)-(\d+)\z/)
      m ? "#{m[2]}-#{m[1]}" : text
    end

    # Mirrors scoreCell() from the original client-side renderer. Group
    # fixtures score on the 90-minute result (3/1/0); knockout fixtures
    # score on the winner pick plus a bonus for the exact 90-minute
    # scoreline (3/2/0), since a draw at 90 minutes is still a valid
    # scoreline prediction but isn't itself the outcome that matters.
    def score_cell(pred, res, f)
      return { "cls" => "noft", "text" => "—", "pts" => nil } unless pred

      text = "#{pred['home_score']}-#{pred['away_score']}"
      return { "cls" => "p-pending", "text" => text, "pts" => nil } unless res

      if f["stage"] == "group"
        if pred["home_score"] == res["home_score"] && pred["away_score"] == res["away_score"]
          { "cls" => "p-exact", "text" => text, "pts" => 3 }
        elsif outcome(pred["home_score"], pred["away_score"]) == outcome(res["home_score"], res["away_score"])
          { "cls" => "p-result", "text" => text, "pts" => 1 }
        else
          { "cls" => "p-wrong", "text" => text, "pts" => 0 }
        end
      elsif pred["winner"] != res["winner"]
        { "cls" => "p-wrong", "text" => text, "pts" => 0 }
      elsif pred["home_score"] == res["home_score"] && pred["away_score"] == res["away_score"]
        { "cls" => "p-exact", "text" => text, "pts" => 3 }
      else
        { "cls" => "p-result", "text" => text, "pts" => 2 }
      end
    end

    def leaderboard(models, fixtures, results)
      tally = models.map { |m| { "model" => m, "scored" => 0, "exact" => 0, "winner" => 0, "result" => 0, "pts" => 0 } }

      fixtures.each do |f|
        res = results[f["id"]]
        next unless res

        tally.each do |t|
          cell = score_cell(t["model"]["by_fixture"][f["id"]], res, f)
          next if cell["pts"].nil?

          t["scored"] += 1
          case cell["pts"]
          when 3 then t["exact"] += 1; t["pts"] += 3
          when 2 then t["winner"] += 1; t["pts"] += 2
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
        cell = score_cell(pred, res, f)
        cell = cell.merge("text" => flip_score(cell["text"])) if transposed
        cell.merge("reasoning" => pred ? (pred["reasoning"] || "") : "")
      end

      outcomes = models.filter_map do |m|
        pred = m["by_fixture"][f["id"]]
        next unless pred
        f["stage"] == "group" ? outcome(pred["home_score"], pred["away_score"]) : pred["winner"]
      end.uniq

      if res
        score_text = transposed ? "#{res['away_score']}-#{res['home_score']}" : "#{res['home_score']}-#{res['away_score']}"
        if f["stage"] != "group" && res["home_score"] == res["away_score"]
          decided = res["decided"] == "pens" ? "pens" : "AET"
          if decided == "pens" && res["pens"]
            pens = transposed ? "#{res['pens']['away_score']}-#{res['pens']['home_score']}" : "#{res['pens']['home_score']}-#{res['pens']['away_score']}"
            ft_text = "#{score_text} (#{decided} #{pens}, #{res['winner']} won)"
          else
            ft_text = "#{score_text} (#{decided}, #{res['winner']} won)"
          end
        else
          ft_text = "#{score_text} FT"
        end
      else
        ft_text = f["date"] || "v"
      end
      ft_class = res ? "ft" : "noft"

      home_code, away_code = transposed ? [f["away"], f["home"]] : [f["home"], f["away"]]

      {
        "id" => f["id"],
        "stage" => f["stage"],
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
