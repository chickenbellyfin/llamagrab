import React, { ChangeEvent } from "react";
import { 
  Form,
  Input,
  InputNumber, 
  Radio, 
  RadioChangeEvent, 
  Switch, 
  Tabs,
  Typography
} from "antd";

import { API, GameServerConfig } from "../../api";

import MapSelector from "./MapSelector";
import Loader from "../Loader";
import Rules from "./validation";

const { TabPane } = Tabs;

type EditorProps = {
  config: GameServerConfig
  onChange?: (config: GameServerConfig) => void
}

type EditorState = {
  config: any,
  isSaving: boolean
}

export class GameServerConfigForm extends React.Component<EditorProps, EditorState> {

  constructor(props: EditorProps) {
    super(props)
    this.state = {
      config: Object.assign({}, props.config),
      isSaving: false
    }
  }

  onUpdate(key: string, value: any) {
    this.setState(
      Object.assign(this.state.config, {[key]: value}),
      () => {
        if (this.props.onChange) {
          this.props.onChange(Object.assign({}, this.state.config))
        }
      }
    )
  }

  render() {
    const config = this.state.config;

    const updateText = (key: string) => {
      return (e: ChangeEvent<HTMLInputElement>) => {
        this.onUpdate(key, e.target.value)
      }
    }

    const updateRadio = (key: string) => {
      return (e: RadioChangeEvent) => {
        this.onUpdate(key, e.target.value)
      }
    }

    const updateBoolean = (key: string) => {
      return (e: boolean) => this.onUpdate(key, e)
    }

    const updateNumber = (key: string) => {
      return (e: number) => this.onUpdate(key, e)
    }

    const updateMapList = (mapList: Array<string>) => {
      this.onUpdate('maps', mapList)
    }

    return (
      <>  
        {/* -------- BASIC INFO -------- */}
        <Tabs defaultActiveKey='basic'>
          <TabPane tab="Basic Settings" key='basic'>
            <Form
              labelCol={{span: 4}}
              wrapperCol={{span: 14}}
              >

              <Form.Item 
                label='Name'
                name='name'
                rules={[Rules.required, Rules.allowedCharacters]}>
                <Input
                  defaultValue={config['displayName']} value={config['displayName']}
                  onChange={updateText('displayName')}/>
              </Form.Item>

              <Form.Item name='description' label='Description' rules={[Rules.allowedCharacters]}>
                <Input 
                  defaultValue={config['description']}
                  onChange={updateText('description')}/>
              </Form.Item>
  
              <Form.Item name='password' label='Server Password' rules={[Rules.allowedCharacters]}>
                <Input.Password
                  defaultValue={config['password']}
                  onChange={updateText('password')}/>
              </Form.Item>
              
              <Form.Item name='adminPassword' label='Admin Password' rules={[Rules.allowedCharacters]}>
                <Input.Password
                  defaultValue={config['adminPassword']}
                  onChange={updateText('adminPassword')}/>
              </Form.Item>
            </Form>
  
          </TabPane>
          
  
          {/* -------- GAME SETTINGS -------- */}
          <TabPane tab="Game Settings" key='game'>
  
          <Form
              labelCol={{span: 4}}
              wrapperCol={{span: 14}}>
            <Form.Item 
              label='Team Assign Type:'>
              <Radio.Group
                defaultValue='balanced'
                buttonStyle='solid'
                value={config['teamAssignType']}
                onChange={updateRadio('teamAssignType')}>
                <Radio.Button value='balanced'>Balanced</Radio.Button>
                <Radio.Button value='unbalanced'>Unbalanced</Radio.Button>
                <Radio.Button value='auto'>Auto Assign</Radio.Button>
              </Radio.Group>
            </Form.Item>

            <Form.Item label='Auto Balance'>
              <Switch 
                defaultChecked
                checked={config['autoBalance']}
                onChange={updateBoolean('autoBalance')} />
            </Form.Item>
  
            <Form.Item label='Time Limit'>
              <InputNumber 
                precision={0}
                min={1}
                value={config['timeLimit']}
                onChange={updateNumber('timeLimit')}
                addonAfter='mins' />
            </Form.Item>          
            
            <Form.Item label='Overtime Limit'>
              <InputNumber
                precision={0}
                min={0}
                value={config['overtimeLimit']}
                onChange={updateNumber('overtimeLimit')}
                addonAfter='mins' />
            </Form.Item>
  
            <Form.Item label='Friendly Fire'>
              <Switch 
                defaultChecked 
                checked={config['friendlyFire']}
                onChange={updateBoolean('friendlyFire')} />
            </Form.Item>
            </Form>
          </TabPane>
  
  
          {/* -------- MAP ROTATION -------- */}
          <TabPane tab="Map Rotation" key='maps'>
          <Form labelCol={{span: 4}} wrapperCol={{span: 14}}>
            <Form.Item label='Map Voting'>
              <Switch defaultChecked onChange={(checked: boolean) => null} />
            </Form.Item>
            <fieldset>
              <legend >
                <MapSelector 
                  gameType='CTF'
                  mapList={config['maps']}
                  onChange={updateMapList}/>
              </legend>
            </fieldset>
          </Form>
          </TabPane>
  
  
          {/* -------- WEAPONS -------- */} 
          <TabPane tab="Weapons" key='weapons'>
            <Form labelCol={{span: 4}} wrapperCol={{span: 14}}>
              <Typography.Title level={2} type="secondary">Coming Soon</Typography.Title>
            </Form>
          </TabPane>
  
  
          {/* -------- VEHICLES -------- */}
          <TabPane tab="Vehicles" key='vehicles'>
            <Form labelCol={{span: 4}} wrapperCol={{span: 14}}>
              
            <Typography.Title level={2} type="secondary">Coming Soon</Typography.Title>
            </Form>
          </TabPane>
        </Tabs>
  
      </>
    )
  }
}

// wrap in a loader to edit an existing config
type EditorLoaderProps = Omit<EditorProps, 'config'> & {serverId:  number}
export const EditGameServerConfigForm = Loader<EditorLoaderProps, GameServerConfig>({
  loaderFunc: (props) => API.Server.getServerConfig(props.serverId),
  componentBuilder: (config, props) => <GameServerConfigForm config={config} {...props} />
})
