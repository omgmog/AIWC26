# Generates one frozen /archive/<stage>/ page per completed stage, so each
# new round (r32, r16, ...) gets an archive automatically once it stops
# being site.data.computed.current_stage -- no per-stage page to hand-write.
module AIWC26
  class ArchivePageGenerator < Jekyll::Generator
    safe true
    priority :normal

    def generate(site)
      computed = site.data["computed"]
      computed["stages"].each_key do |key|
        next if key == computed["current_stage"]

        page = Jekyll::PageWithoutAFile.new(site, site.source, "archive/#{key}", "index.html")
        page.data["layout"] = "archive"
        page.data["stage_key"] = key
        page.data["archive"] = true
        page.data["permalink"] = "/archive/#{key}/"
        site.pages << page
      end
    end
  end
end
