<template>
  <div class="order-file-list">
    <div class="order-file-buttons" v-if="sortedFiles.length > 0">
      <button @click="sort('size')" class="order-file-button">
        size<i
          :class="[
            'fas',
            'fa-sort-' + (order.size === 'asc' ? 'amount-up' : 'amount-down'),
          ]"
        ></i>
      </button>
      <button @click="sort('name')" class="order-file-button">
        name<i
          :class="[
            'fas',
            'fa-sort-' + (order.name === 'asc' ? 'amount-up' : 'amount-down'),
          ]"
        ></i>
      </button>
      <button @click="sort('date')" class="order-file-button">
        date<i
          :class="[
            'fas',
            'fa-sort-' + (order.date === 'asc' ? 'amount-up' : 'amount-down'),
          ]"
        ></i>
      </button>
      <button
        @click="viewMode = 'card'"
        class="order-file-button"
        id="order-file-button-card-view"
      >
        <i class="fas fa-th-large"></i>Card
      </button>
      <button @click="viewMode = 'list'" class="order-file-button">
        <i class="fa-solid fa-list"></i>List
      </button>
    </div>

    <div :style="listStyle">
      <div v-for="file in sortedFiles" :key="file.id">
        <FileItemComponent :file="file" :viewMode="viewMode" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from "vue";
import FileItemComponent from "./FileItemComponent.vue";
import store from "../store";

export default {
  props: {
    files: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      viewMode: "list",
    };
  },
  components: {
    FileItemComponent,
  },
  computed: {
    listStyle() {
      if (this.viewMode === "card") {
        store.commit("changeViewMode", "card");
        return {
          display: "flex",
          flexWrap: "wrap",
          padding: 0,
        };
      } else if (this.viewMode === "list") {
        store.commit("changeViewMode", "list");
        return {
          display: "inline",
          "flex-wrap": "nowrap",
          padding: 0,
        };
      } else {
        return {
          display: "inline",
          "flex-wrap": "nowrap",
          padding: 0,
        };
      }
    },
  },
  setup(props) {
    const sortBy = ref("name");
    const order = ref({ size: "asc", name: "asc", date: "asc" });

    const sort = (key) => {
      sortBy.value = key;
      order.value[key] = order.value[key] === "asc" ? "desc" : "asc";
    };

    let sortedFiles = computed(() => {
      return [...props.files].sort((a, b) => {
        let comparison = 0;

        switch (sortBy.value) {
          case "size":
            comparison = a.file_size - b.file_size;
            break;
          case "name":
            comparison = a.filename.localeCompare(b.filename);
            break;
          case "date":
            comparison =
              new Date(a.file_create_time) - new Date(b.file_create_time);
            break;
        }

        return order.value[sortBy.value] === "desc" ? -comparison : comparison;
      });
    });

    return { sortedFiles, sort, order };
  },
};
</script>

<style scoped>
.order-file-buttons {
  margin-bottom: 10px;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
}

.order-file-button {
  background-color: #1a7be3;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 5px 10px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  width: 100%;
  height: 2.3rem;
  text-align: center;
}

.order-file-button:hover {
  background-color: #16723c;
}

/* 媒体查询 */
@media (max-width: 600px) {
  #order-file-button-card-view {
    display: none;
  }
}
</style>
