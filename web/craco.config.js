/* https://ant.design/docs/react/use-with-create-react-app */
const CracoLessPlugin = require('craco-less');
const babelInclude = require('@dealmore/craco-plugin-babel-include');

// THIS MIGHT BE MAKING LESS WORK DONT TOUCH IT FOR NOW
module.exports = {
  plugins: [
    {
      plugin: CracoLessPlugin,
      options: {
        lessLoaderOptions: {
          lessOptions: {
            javascriptEnabled: true,
          },
        },
      },
    },
    {
      plugin: babelInclude,
      options: {
        include: ['../../common'],
      },
    },
  ],
  // webpack: {
  //   configure: {
  //     devtool: 'eval-source-map'
  //   }
  // }
};