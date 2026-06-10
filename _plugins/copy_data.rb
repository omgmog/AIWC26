# Publishes _data/ verbatim as /data/ in the built site, so fixtures.json,
# manifest.json, results.json and predictions/*.json keep their original
# URLs as the project's public API and audit trail.
require "fileutils"

Jekyll::Hooks.register :site, :post_write do |site|
  src = File.join(site.source, "_data")
  dest = File.join(site.dest, "data")
  FileUtils.rm_rf(dest)
  FileUtils.cp_r(src, dest)
end
