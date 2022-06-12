import React from "react";
import { Tabs } from "antd";

import { API, GameServerConfig } from "../../api";

import { createUpdateCallbacks } from "../tabHelpers";
import GameSettingsTab from "./GameSettingsTab";
import MapRotationSettingsTab from "./MapRotationSettingsTab";
import BasicSettingsTab from "./BasicSettingsTab";
import WeaponsSettingsTab from "./WeaponsSettingsTab";
import VehicleSettingsTab from "./VehicleSettingsTab";
import TeamSettingsTab from "./TeamSettingsTab";
import PlayerSettingsTab from "./PlayerSettingsTab";
import ValueModsTab from "./ValueModsTab";
import { EditorProps } from "../Editor";

const { TabPane } = Tabs;

type EditorState = {
  config: GameServerConfig,
  isSaving: boolean
}

export default class TribesAscendGOTYEditorForm extends React.Component<EditorProps, EditorState> {

  constructor(props: EditorProps) {
    super(props)
    this.state = {
      config: Object.assign({}, props.config),
      isSaving: false
    }
  }

  onUpdate = (key: string, value: any) => {
    this.setState(
      Object.assign(this.state.config as any, {[key]: value}),
      () => {
        if (this.props.onChange) {
          this.props.onChange(this.state.config)
        }
      }
    )
  }

  render() {
    const updateCallbacks = createUpdateCallbacks(this.onUpdate)
    return (
      <>
        <Tabs defaultActiveKey='basic'>
          <TabPane tab="Basic Settings" key='basic'>
            <BasicSettingsTab config={this.state.config} updateCallbacks={updateCallbacks}/>
          </TabPane>

          <TabPane tab="Game Settings" key='game'>
            <GameSettingsTab config={this.state.config} updateCallbacks={updateCallbacks}/>
          </TabPane>

          <TabPane tab="Team Settings" key='team'>
            <TeamSettingsTab config={this.state.config} updateCallbacks={updateCallbacks}/>
          </TabPane>

          <TabPane tab="Map Rotation" key='maps'>
            <MapRotationSettingsTab config={this.state.config} updateCallbacks={updateCallbacks}/>
          </TabPane>

          <TabPane tab="Vehicles" key='vehicles'>
            <VehicleSettingsTab config={this.state.config} updateCallbacks={updateCallbacks}/>
          </TabPane>

          <TabPane tab="Value Mods" key='value_mods'>
            <ValueModsTab config={this.state.config} updateCallbacks={updateCallbacks}/>
          </TabPane>
        </Tabs>
      </>
    )
  }
}
