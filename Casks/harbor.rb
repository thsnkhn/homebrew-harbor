cask "harbor" do
  version "1.7.8"
  sha256 "a5edbeb813e75aacbd3816dd21108759ff63ecd5d2fbcb8ae1cb4057f82c58f9"

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
