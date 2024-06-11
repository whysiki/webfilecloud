<template>
  <div ref="chart" style="width: 100%; height: 400px"></div>
</template>

<script>
import * as echarts from "echarts";

export default {
  props: {
    allFilesSize: Number,
    typesSizeCount: Object,
  },
  mounted() {
    this.initChart();
  },
  methods: {
    formatSize(size) {
      if (size < 1024) {
        return `${size} B`;
      } else if (size < 1024 * 1024) {
        return `${(size / 1024).toFixed(2)} KB`;
      } else if (size < 1024 * 1024 * 1024) {
        return `${(size / 1024 / 1024).toFixed(2)} MB`;
      } else {
        return `${(size / 1024 / 1024 / 1024).toFixed(2)} GB`;
      }
    },
    initChart() {
      const chart = echarts.init(this.$refs.chart);
      const option = {
        title: {
          text: `File Size ToTal : ${this.formatSize(this.allFilesSize)}`,
        },
        tooltip: {
          trigger: "item",
        },
        series: [
          {
            name: "File Size",
            type: "pie",
            radius: "50%",
            data: Object.keys(this.typesSizeCount).map((key) => ({
              value: this.typesSizeCount[key],
              name: key,
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: "rgba(0, 0, 0, 0.5)",
              },
            },
          },
        ],
      };
      chart.setOption(option);
    },
  },
};
</script>

<style scoped></style>
