import React from "react"
import { API, GameServerConfig } from "../api"
import Loader from "../components/Loader"
import { TribesAscendEditorForm } from "./tribes_ascend/TribesAscendEditorForm"

export type EditorProps = {
  config: GameServerConfig
  onChange?: (config: GameServerConfig) => void
}

// wrap in a loader to edit an existing config
type EditorLoaderProps = Omit<EditorProps, 'config'> & {
  serverId:  number,
}
export const EditorLoader = Loader<EditorLoaderProps, GameServerConfig>({
  loaderFunc: (props) => API.Server.getServerConfig(props.serverId),
  componentBuilder: (config, props: EditorLoaderProps) => <TribesAscendEditorForm config={config} {...props} />
})
