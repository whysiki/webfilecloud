<template>
  <div class="order-file-list">
    <div class="order-file-buttons">
      <button @click="sort('size')" class="order-file-button">
        Sort by size
        <i
          :class="[
            'fas',
            'fa-sort-' + (order.size === 'asc' ? 'amount-up' : 'amount-down'),
          ]"
        ></i>
      </button>
      <button @click="sort('name')" class="order-file-button">
        Sort by name
        <i
          :class="[
            'fas',
            'fa-sort-' +
              (order.name === 'asc' ? 'alphabet-up' : 'alphabet-down'),
          ]"
        ></i>
      </button>
      <button @click="sort('date')" class="order-file-button">
        Sort by date
        <i
          :class="[
            'fas',
            'fa-sort-' + (order.date === 'asc' ? 'amount-up' : 'amount-down'),
          ]"
        ></i>
      </button>
    </div>

    <div :style="listStyle">
      <div v-for="file in sortedFiles" :key="file.id">
        <FileItemComponent :file="file" />
      </div>
    </div>
  </div>
</template>

<script>
import { inject, ref, computed } from "vue";
import FileItemComponent from "./FileItemComponent.vue";
import store from "../store";

export default {
  props: {
    files: {
      type: Array,
      required: false,
    },
  },
  components: {
    FileItemComponent,
  },
  computed: {
    listStyle() {
      if (store.state.viewMode === "card") {
        return {
          display: "flex",
          flexWrap: "wrap",
          padding: 0,
        };
      } else if (store.state.viewMode === "list") {
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
    // const files = files || inject("files");
    // const files = props.files || inject("files");
    const files = ref(props.files || inject("files"));
    const sortBy = ref("name");
    const order = ref({ size: "asc", name: "asc", date: "asc" });

    const sort = (key) => {
      sortBy.value = key;
      order.value[key] = order.value[key] === "asc" ? "desc" : "asc";
    };

    const sortedFiles = computed(() => {
      return [...files.value].sort((a, b) => {
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
.order-file-list {
  margin-top: 20px;
}

.order-file-buttons {
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
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
  text-align: center;
}

.order-file-button:hover {
  background-color: #16723c;
}

.fa-sort-amount-up,
.fa-sort-amount-down,
.fa-sort-alphabet-up,
.fa-sort-alphabet-down {
  margin-left: 5px;
}

@media (min-width: 768px) {
  .order-file-buttons {
    flex-direction: row;
    justify-content: space-evenly;
  }

  .order-file-button {
    width: auto;
  }
}
</style>
