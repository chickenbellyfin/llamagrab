import { GameServerConfig } from "../api"
import { TribesAscendEditorForm } from "./tribes_ascend/TribesAscendEditorForm";

import defaultOOTBConfig from '../../../common/default.json'
import TribesAscendGOTYEditorForm from "./tribes_ascend/TribesAscendGOTYEditorForm";

export default {
    'tribes_ascend_ootb': {
        title: 'Tribes Ascend',
        editor: TribesAscendEditorForm,
        defaultConfig: defaultOOTBConfig as GameServerConfig
    },
    'tribes_ascend_goty': {
        title: 'Tribes Ascend GOTY',
        editor: TribesAscendGOTYEditorForm,
        defaultConfig: {} as GameServerConfig
    }
};