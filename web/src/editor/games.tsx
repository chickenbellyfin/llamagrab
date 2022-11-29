import defaultGOTYConfig from '../../../resources/defaults/tribes_ascend_goty.json';
import defaultOOTBConfig from '../../../resources/defaults/tribes_ascend_ootb.json';
import { GameServerConfig, GameType } from '../domain';
import { EditorProps } from "./Editor";
import TribesAscendEditorForm from "./tribes_ascend/TribesAscendEditorForm";
import TribesAscendGOTYEditorForm from "./tribes_ascend/TribesAscendGOTYEditorForm";


type GameSpec = {
  title: string
  short: string
  editor: React.ComponentType<EditorProps>
  defaultConfig: GameServerConfig
}

type GameSpecMap = { [key in GameType]: GameSpec }

const games: GameSpecMap = {
  'tribes_ascend_ootb': {
    title: 'Tribes Ascend',
    short: 'OOTB',
    editor: TribesAscendEditorForm,
    defaultConfig: defaultOOTBConfig as GameServerConfig
  },
  'tribes_ascend_goty': {
    title: 'Tribes Ascend GOTY',
    short: 'GOTY',
    editor: TribesAscendGOTYEditorForm,
    defaultConfig: defaultGOTYConfig as GameServerConfig
  }
};

export default games;
