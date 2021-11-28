import { ChangeEvent } from "react";
import { 
  RadioChangeEvent, 
} from "antd";
import { GameServerConfig } from "../../api";

type ChangeEventHandler = (e: ChangeEvent<HTMLInputElement>) => void
type RadioChangeEventHandler = (e: RadioChangeEvent) => void

export type GameServerConfigTabProps = {
  config: GameServerConfig,
  updateCallbacks: UpdateCallbacks
}

export type UpdateCallbacks = {
  updateInput: (key: string) => ChangeEventHandler
  updateRadio: (key: string) => RadioChangeEventHandler
  updateSwitch: (key: string) => (value: boolean) => void
  updateInputNumber: (key: string) => (value: number) => void
  update: (key: string) => (value: any) => void
};

/*
This is a helper for creating onChange callbacks for form fields. 
UpdateCallbacks is a set of helper functions which takes a config key and returns a callback function
which takes the onChange arg for that input and calls updateHandler with the value
*/
export function createUpdateCallbacks(updateHandler: (key: string, value: any) => void): UpdateCallbacks {
  return {
    updateInput: (key) => (event) => updateHandler(key, event.target.value),
    updateRadio: (key) => (event) => updateHandler(key, event.target.value),
    updateSwitch: (key) => (value) => updateHandler(key, value),
    updateInputNumber: (key) => (value) => updateHandler(key, value),
    update: (key) => (value) => updateHandler(key, value),
  };
}