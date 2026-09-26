cask "harbor" do
  version "1.8.1"
  sha256 "d6e4176271538f332709cf0ce1dcb60aaba32a62932e2ce1dd8464996c6e42f3"

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
