cask "harbor" do
  version "1.8.6"
  sha256 "174beb130dd2b457eba1f14024272b02ac86167b12b6cf54145937cdc5285f0d"

  url "https://github.com/thsnkhn/harbor/releases/download/v#{version}/Harbor-#{version}.dmg"
  name "Harbor"
  desc "Download manager for URLs, magnet links, and torrent files"
  homepage "https://github.com/thsnkhn/harbor"

  livecheck do
    url :url
    strategy :github_latest
  end

  auto_updates true
  depends_on macos: :sequoia

  app "Harbor.app"

  zap trash: [
    "~/Library/Application Support/Harbor",
    "~/Library/Caches/co.hapy.harbor",
    "~/Library/HTTPStorages/co.hapy.harbor",
    "~/Library/Preferences/co.hapy.harbor.plist",
    "~/Library/Saved Application State/co.hapy.harbor.savedState",
  ]
end
