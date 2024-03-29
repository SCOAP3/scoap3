const { merge } = require('webpack-merge');
const commonConfig = require('./common.config');

// This variable should mirror the one from config/settings/production.py
const s3BucketName = process.env.DJANGO_AWS_STORAGE_BUCKET_NAME;
const s3Url = process.env.DJANGO_AWS_S3_CUSTOM_DOMAIN ? `${s3BucketName}.${process.env.DJANGO_AWS_S3_CUSTOM_DOMAIN}` : null;

const staticUrl =  s3Url ? `https://${s3Url}/static/` : '/static/';

module.exports = merge(commonConfig, {
  mode: 'production',
  devtool: 'source-map',
  bail: true,
  output: {
    publicPath: `${staticUrl}webpack_bundles/`,
  },
});
