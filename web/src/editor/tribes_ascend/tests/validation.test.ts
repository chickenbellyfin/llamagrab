import {allowedCharactersRegex} from '../validation'

test('allow allowed characters', () => {
  expect(allowedCharactersRegex.test(' ')).toEqual(true)
  expect(allowedCharactersRegex.test("[CLAN] *MY server's, 0* | status:yes w/o/w")).toEqual(true)
  expect(allowedCharactersRegex.test('llamagrab.net')).toEqual(true)
})

test('Don\'t allow disallowed characters', () => {

  expect(allowedCharactersRegex.test('not;allowed')).toEqual(false)
  expect(allowedCharactersRegex.test('not)allowed')).toEqual(false)
  expect(allowedCharactersRegex.test('not(allo)wed')).toEqual(false)
  expect(allowedCharactersRegex.test('no"t allowed')).toEqual(false)
})