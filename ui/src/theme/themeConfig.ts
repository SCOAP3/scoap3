import type { ThemeConfig } from 'antd';

const theme: ThemeConfig = {
  token: {
    fontSize: 16,
    colorTextPlaceholder: '#777',
    fontFamily: '"PT Sans Narrow", sans-serif'
  },
  components: {
    Slider: {
      handleColor: "#3498db",
      handleSize: 7,
      handleSizeHover: 10,
      handleLineWidthHover: 2,
      railSize: 3,
    },
  }
};

export default theme;
