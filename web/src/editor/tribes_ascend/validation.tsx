import { Rule } from "antd/lib/form";

export const allowedCharactersRegex = /^[a-zA-Z0-9 _\-:/,*|[\]]+$/;

const Rules = {
  required: {required: true, message: 'Required'} as Rule,
  allowedCharacters: {  type: 'string', pattern: allowedCharactersRegex, message:'Allowed characters: a-z, 0-9, _-:/,*|[]'} as Rule
}

export default Rules;