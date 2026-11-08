cask "harbor" do
  arch arm: "Apple-Silicon", intel: "Intel"
  version "1.9.1"

  on_arm do
    sha256 "04f6216f539c800279e887b2fa1ce48c40be319dbb7be06243295f4a7095b730"
  end
  on_intel do
    sha256 "f38003ae1ef6d4a2f2125852eedc2ab42c26bbd4b8d8915d8d1bf074ed2c13a3"
  end

  url "https://github.com/thsnkhn/harbor/releases/download/v#{version}/Harbor-#{version}-#{arch}.dmg"
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
