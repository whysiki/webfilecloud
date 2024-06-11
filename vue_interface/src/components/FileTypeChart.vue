<template>
  <div ref="chart" style="width: 100%; height: 400px"></div>
</template>

<script>
import * as echarts from "echarts";

export default {
  props: {
    typesCount: Object,
  },
  mounted() {
    this.initChart();
  },
  methods: {
    initChart() {
      const chart = echarts.init(this.$refs.chart);
      const option = {
        title: {
          text: `File Type Count: ${Object.keys(this.typesCount).length} class`,
        },
        tooltip: {},
        xAxis: {
          type: "category",
          data: Object.keys(this.typesCount),
        },
        yAxis: {
          type: "value",
        },
        series: [
          {
            type: "bar",
            data: Object.values(this.typesCount),
            itemStyle: {
              color: (params) => {
                const colors = [
                  "#5470C6",
                  "#91CC75",
                  "#FAC858",
                  "#EE6666",
                  "#73C0DE",
                  "#3BA272",
                  "#FC8452",
                  "#9A60B4",
                  "#EA7CCC",
                ];
                return colors[params.dataIndex % colors.length];
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
