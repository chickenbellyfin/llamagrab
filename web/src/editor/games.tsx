import { GameServerConfig, GameType } from "../api"
import { TribesAscendEditorForm } from "./tribes_ascend/TribesAscendEditorForm";

import defaultOOTBConfig from '../../../common/default.json'
import { EditorProps } from "./Editor";

export default {
    'tribes_ascend_ootb': {
        title: 'Tribes Ascend',
        editor: TribesAscendEditorForm,
        defaultConfig: defaultOOTBConfig as GameServerConfig
    },
    'tribes_ascend_goty': {
        title: 'Tribes Ascend GOTY',
        editor: (props: EditorProps) => <b>Editing Goty</b>,
        defaultConfig: {} as GameServerConfig
    }
};