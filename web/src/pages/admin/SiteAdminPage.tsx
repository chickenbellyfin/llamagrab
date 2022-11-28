import { Button, Card, Form, Input, message, PageHeader, Popconfirm, Select, Spin, Switch } from "antd";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API } from "../../api";
import ContentWrapper from "../../components/ContentWrapper";
import useLoader from "../../useLoader";



export default function SiteAdminPage() {
  const flagsLoader = useLoader(API.Admin.Site.getSiteFlags)
  const loginserversLoader = useLoader(API.Data.getLoginservers)
  const [actionInProgress, setActionInProgress] = useState(false)
  const navigate = useNavigate()

  const onUpdateFlag = async (key: string, newValue: any) => {
    try {
      await API.Admin.Site.setSiteFlag(key, newValue)
      message.success("Flag Updated")
    } catch {
      message.error("Flag Update Failed")
    } finally {
      flagsLoader.invalidate()
    }
  }

  const onRequestSync = async () => {
    setActionInProgress(true)
    try {
      await API.Admin.Site.requestSync()
      message.success("Sync Requested")
    } catch {
      message.error("Sync Request Failed")
    } finally {
      setActionInProgress(false)
    }
  }

  const onRestartAll = async () => {
    setActionInProgress(true)
    try {
      const count = await API.Admin.Site.restartAllServers()
      message.success(`Triggered restart of ${count} servers`)
    } catch {
      message.error("Restart all failed")
    } finally {
      setActionInProgress(false)
    }
  }

  const onDisableAll = async () => {
    setActionInProgress(true)
    try {
      const count = await API.Admin.Site.disableAllServers()
      message.success(`Disabled ${count} active servers`)
    } catch {
      message.error("Disable all failed")
    } finally {
      setActionInProgress(false)
    }
  }

  return (
    <ContentWrapper>
      <PageHeader title={<span className="ui-title">Site Settings</span>} onBack={() => navigate('/')} />

      <Spin spinning={flagsLoader.initialLoad}>
        <Card title="Flags" style={{marginBottom: '10px'}}>
          <Form>
            <Form.Item label="Disable New Account Creation">
              <Switch 
                checked={flagsLoader.value ? flagsLoader.value['disable_new_accounts'] : false} 
                onChange={(value) => onUpdateFlag('disable_new_accounts', value)}/>
            </Form.Item>

            <Form.Item label="Disable Un-Verified Users"
              extra="All unverified-tier users will be unable to log in or make changes.">
              <Switch
                checked={flagsLoader.value? flagsLoader.value['disable_unverified_accounts'] : false} 
                onChange={(value) => onUpdateFlag('disable_unverified_accounts', value)}/>
            </Form.Item>

            <Form.Item label="Disable Non-Admin Users"
              extra="All users other than Admin+ (including unverified) will be unable to log in or make changes.">
              <Switch
                checked={flagsLoader.value? flagsLoader.value['disable_non_admin_accounts'] : false} 
                onChange={(value) => onUpdateFlag('disable_non_admin_accounts', value)}/>
            </Form.Item>

            <Form.Item label="Login Server"
              extra='Set the loginserver URL for all servers. Must "Request Sync" after changing this setting'>
              <Select
                defaultValue=""
                value={flagsLoader.value ? flagsLoader.value['loginserver'] : ""}
                style={{ width: 230 }}
                onChange={(value) => onUpdateFlag('loginserver', value)}
                options={
                  loginserversLoader.value ? 
                    loginserversLoader.value.map(item => { 
                      return {value: item.url, label: item.name}
                    })
                    :
                    []
                }
              />
            </Form.Item>
          </Form>
        </Card>
      </Spin>

      <Spin spinning={actionInProgress}>
        <Card title="Actions" style={{marginBottom: '10px'}}>
          <Form
            labelCol={{ span: 6 }}
            wrapperCol={{ span: 14 }}>

            <Form.Item 
            label="Request Sync"
            extra="Re-generate all server configs. Will update & restart any mismatching servers.">
                <Button type="primary" onClick={onRequestSync}>
                    Sync
                </Button>
            </Form.Item>

            <Form.Item 
              label="Restart All Servers"
              extra="Force re-create all servers with their current config. (Do Not Spam)">
              <Popconfirm 
              title="All servers will be restarted immediately. Regions with a lot of servers may become unstable."
              onConfirm={onRestartAll}>
                <Button type="primary" danger>Restart</Button>
              </Popconfirm>
            </Form.Item>

            <Form.Item 
              label="Disable All Servers"
              extra="Stop all enabled servers.">
              <Popconfirm 
              title="All servers will be shut down and must be manually started. Are you sure?"
              onConfirm={onDisableAll}>
                <Button type="primary" danger>Disable</Button>
              </Popconfirm>
            </Form.Item>
          </Form>
        </Card>
      </Spin>


    </ContentWrapper>
  );
}
