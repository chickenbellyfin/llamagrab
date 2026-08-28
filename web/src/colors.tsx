import { presetDarkPalettes } from '@ant-design/colors';
import { CSSProperties } from 'react';

const palettes = presetDarkPalettes;

// colors for user tier badges
const tierColors: {[key: string]: any} = {
  'super': 'red',
  'admin': 'purple',
  'verified': 'green',
  'unverified': ''
}

const colors = {
  success: {
    hex: palettes.green[6],
    style: { color: palettes.green[6] } as CSSProperties
  },
  warning: {
    hex: palettes.gold[6],
    style: { color: palettes.gold[6] } as CSSProperties
  },
  error: {
    hex: palettes.red[5],
    style: { color: palettes.red[5] } as CSSProperties
  },
  disabled: {
    hex: '#bfbfbf',
    style: { color: '#bfbfbf' } as CSSProperties
  },
  componentBackground: {
    hex: '#383e47'
  },
  popoverBackground: {
    hex: '#404854'
  },
  tiers: tierColors
};

export default colors;
