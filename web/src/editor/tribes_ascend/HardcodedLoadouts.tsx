import { Form, Select, Switch, Table } from "antd";
import { ColumnsType } from "antd/es/table";
import { useEffect, useState } from "react";
import { PlayerClass, weaponOptions } from "../../data";
import './HardcodedLoadouts.less'
import { UpdateCallbacks } from "../../editor/tabHelpers";
import { GameServerConfig, HardcodedLoadout } from "../../domain";

const allSlots = [0, 1, 2, 3, 4, 5, 6, 7, 8];

const loadoutOptions = {
  'Light': {
    guns: weaponOptions('Light', ['impact', 'timed', 'chain', 'specialty']),
    belt: weaponOptions('Light', ['belt']),
    pack: weaponOptions('Light', ['pack'])
  },
  'Medium': {
    guns: weaponOptions('Medium', ['impact', 'timed', 'chain', 'specialty']),
    belt: weaponOptions('Medium', ['belt']),
    pack: weaponOptions('Medium', ['pack'])
  },
  'Heavy': {
    guns: weaponOptions('Heavy', ['impact', 'timed', 'chain', 'specialty']),
    belt: weaponOptions('Heavy', ['belt']),
    pack: weaponOptions('Heavy', ['pack'])
  }
}

function hardcodedLoadoutEqual(a: HardcodedLoadout, b: HardcodedLoadout): boolean {
  return (
    a.primary === b.primary &&
    a.secondary === b.secondary &&
    a.tertiary === b.tertiary &&
    a.belt === b.belt &&
    a.pack === b.pack
  );
}

interface ClassHardcodedLoadoutsProps {
  clazz: PlayerClass,
  hardcodedLoadouts?: HardcodedLoadout[],
  onChange: (value: HardcodedLoadout[]) => void
}
interface ClassHardcodedLoadoutsState {
  perSlot: boolean
  hardcodedLoadouts: HardcodedLoadout[]
}
function ClassHardcodedLoadouts(props: ClassHardcodedLoadoutsProps) {

  let isPropsPerSlot = false;
  if (props.hardcodedLoadouts) {
    // if all hardcoded loadouts are not the same, it is per slot
    isPropsPerSlot = !props.hardcodedLoadouts.every(item => {
      return props.hardcodedLoadouts && hardcodedLoadoutEqual(item, props.hardcodedLoadouts[0])
    });
  }

  const [state, setState] = useState<ClassHardcodedLoadoutsState>({
    perSlot: isPropsPerSlot,
    hardcodedLoadouts: allSlots.map((idx) => {
      if (props.hardcodedLoadouts && props.hardcodedLoadouts[idx]) {
        return props.hardcodedLoadouts[idx]
      } else {
        return {}
      }
    })
  });

  useEffect(() => {
    // deep copy
    const updated = state.hardcodedLoadouts.map(item => Object.assign({}, item))
    // if its not per-slot, set all values to the first loadout
    if (!state.perSlot) {
      allSlots.forEach(idx => updated[idx] = state.hardcodedLoadouts[0])
    }
    props.onChange(updated)
  }, [state]);

  const setPerSlot = (value: boolean) => {
    setState(Object.assign({}, state, {perSlot: value}))
  }

  const updateWeapon = (slot: number, equipPoint: keyof HardcodedLoadout, weapon?: string) => {
    weapon = (weapon == 'none') ? undefined : weapon;
    // deep copy
    const updatedLoadouts = state.hardcodedLoadouts.map(item => Object.assign({}, item))
    updatedLoadouts[slot][equipPoint] = weapon;
    setState(Object.assign({}, state, {hardcodedLoadouts: updatedLoadouts}))
  }

  const slotColumn: ColumnsType<any> = state.perSlot ? [{title: '#', width: '5%'}] : [];
  const weaponColumns: ColumnsType<any> = [
    {
      title: 'Primary',
      render: (slot: number) => {
        return (
          <Select
            allowClear
            value={state.hardcodedLoadouts[slot].primary}
            onChange={(value: string) => updateWeapon(slot, 'primary', value)}>
            {loadoutOptions[props.clazz].guns}
          </Select>
        );
      }
    },
    {
      title: 'Secondary',
      render: (slot: number) => {
        return (
          <Select
            allowClear
            value={state.hardcodedLoadouts[slot].secondary}
            onChange={(value: string) => updateWeapon(slot, 'secondary', value)}>
            {loadoutOptions[props.clazz].guns}
          </Select>
        );
      }
    },
    {
      title: 'Tertiary',
      render: (slot: number) => {
        return (
          <Select
            allowClear
            value={state.hardcodedLoadouts[slot].tertiary}
            onChange={(value: string) => updateWeapon(slot, 'tertiary', value)}>
            {loadoutOptions[props.clazz].guns}
          </Select>
        );
      }
    },
    {
      title: 'Belt',
      render: (slot: number) => {
        return (
          <Select
            allowClear
            value={state.hardcodedLoadouts[slot].belt}
            onChange={(value: string) => updateWeapon(slot, 'belt', value)}>
            {loadoutOptions[props.clazz].belt}
          </Select>
        );
      }
    },
    {
      title: 'Pack',
      render: (slot: number) => {
        return (
          <Select
            allowClear
            value={state.hardcodedLoadouts[slot].pack}
            onChange={(value: string) => updateWeapon(slot, 'pack', value)}>
            {loadoutOptions[props.clazz].pack}
          </Select>
        );
      }
    }
  ];

  const rows = state.perSlot ? [0, 1, 2, 3, 4, 5, 6, 7, 8] : [0]

  const loadoutColumns: any[] = [
    {
      title: (
        <>
        <span style={{float: 'left'}}>
          {`${props.clazz} Hardcoded Loadouts`}
          {!state.perSlot && <span style={{opacity:'50%'}}> (Applies to all loadout slots)</span>}
        </span>
        <span style={{float: 'right'}}>Per-Slot: <Switch checked={state.perSlot} onChange={setPerSlot}/></span>
        </>),
      children: slotColumn.concat(weaponColumns)
    }
  ];


  return (
    <>
      <Table<any> className='ClassHardcodedLoadouts' size='small' tableLayout='fixed' pagination={false} columns={loadoutColumns} dataSource={rows}/>
    </>
  );
}

interface HardcodedLoadoutFormProps {
  config: GameServerConfig,
  updateCallbacks: UpdateCallbacks
}
export default function HardcodedLoadoutsForm ({config, updateCallbacks}: HardcodedLoadoutFormProps) {

  const [enabled, setEnabled] = useState<boolean>(
    config.lightHardcodedLoadouts != undefined
    || config.mediumHardcodedLoadouts != undefined
    || config.heavyHardcodedLoadouts != undefined
  )

  const onToggle = (value: boolean) => {
    if (!value) {
      // if forceHardcodedLoadouts is false, remove hardcoded loadouts
      updateCallbacks.update('lightHardcodedLoadouts')(undefined);
      updateCallbacks.update('mediumHardcodedLoadouts')(undefined);
      updateCallbacks.update('heavyHardcodedLoadouts')(undefined);
    }
    updateCallbacks.update('forceHardcodedLoadouts')(value)
    setEnabled(value);
  }

  return (
    <>
      <Form.Item label='Force Hardcoded Loadouts'>
        <Switch checked={enabled} onChange={onToggle}/>
      </Form.Item>
      { enabled &&
        <Form.Item wrapperCol={{span: 24}}>
          <ClassHardcodedLoadouts
            clazz='Light'
            hardcodedLoadouts={config.lightHardcodedLoadouts}
            onChange={updateCallbacks.update('lightHardcodedLoadouts')}/>
          <ClassHardcodedLoadouts
            clazz='Medium'
            hardcodedLoadouts={config.mediumHardcodedLoadouts}
            onChange={updateCallbacks.update('mediumHardcodedLoadouts')}/>
          <ClassHardcodedLoadouts
            clazz='Heavy'
            hardcodedLoadouts={config.heavyHardcodedLoadouts}
            onChange={updateCallbacks.update('heavyHardcodedLoadouts')}/>
        </Form.Item>
      }
    </>
  );
}