import { GameServerConfig } from "../domain"

export type EditorProps = {
  config: GameServerConfig
  onChange?: (config: GameServerConfig) => void
}
