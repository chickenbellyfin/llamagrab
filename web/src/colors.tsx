import { presetDarkPalettes } from '@ant-design/colors'
import { CSSProperties } from 'react';

const colors = presetDarkPalettes;

export default {
  success: {
    hex: colors.green[6],
    style: { color: colors.green[6] } as CSSProperties
  },
  warning: {
    hex: colors.gold[6],
    style: { color: colors.gold[6] } as CSSProperties
  },
  error: {
    hex: colors.red[5],
    style: { color: colors.red[5] } as CSSProperties
  },
  disabled: {
    hex: '#bfbfbf',
    style: { color: '#bfbfbf' } as CSSProperties
  }
}
