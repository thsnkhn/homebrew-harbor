cask "harbor" do
  arch arm: "Apple-Silicon", intel: "Intel"
  version "1.9.0"

  on_arm do
    sha256 "f79448df9a2ed618cdac752fc482b134f0aa6f7960d25f0744bdf06a9be69950"
  end
  on_intel do
    sha256 "412792360d149a71a63b03b14dd66347712bad0d61f8068f8ff41c7618dfd164"
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
