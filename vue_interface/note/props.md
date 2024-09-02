## props

在 Vue 中，父组件可以通过 props 将数据传递给子组件。props 是子组件的属性，它们由父组件传递给子组件，并且子组件可以在其内部使用这些属性的值。让我们看一下具体的实现方式：

在父组件中，当使用子组件时，可以通过在子组件标签上添加属性来传递数据。例如：

```vue
<template>
  <div>
    <!-- 父组件中的数据通过属性的形式传递给子组件 -->
    <ChildComponent :propName="parentData" />
  </div>
</template>

<script>
import ChildComponent from "./ChildComponent.vue";

export default {
  components: {
    ChildComponent,
  },
  data() {
    return {
      parentData: "This is data from parent component",
    };
  },
};
</script>
```

在上面的例子中，`parentData` 是父组件中的数据，它通过 `propName` 这个属性传递给了子组件 `ChildComponent`。在子组件中，我们可以通过定义 `props` 来接收这个数据：

```vue
<template>
  <div>
    <!-- 子组件中通过 props 接收父组件传递的数据 -->
    <p>{{ propName }}</p>
  </div>
</template>

<script>
export default {
  props: {
    propName: {
      type: String,
      required: true,
    },
  },
};
</script>
```

在子组件中，我们使用了 `props` 对象来定义接收的属性，其中 `propName` 是父组件传递过来的属性名称。在这个例子中，子组件就可以使用 `propName` 这个属性来获取父组件传递的数据了。

因此，原始组件可以通过在子组件标签上添加属性的方式，将数据传递给子组件。子组件则可以通过定义 `props` 来接收这些数据，并在内部使用。

```html
<TypesComponent
  v-for="fileType in fileTypes"
  :key="fileType"
  :fileType="fileType"
  :visibleFileTypes="visibleFileTypes"
  :files="files"
  @toggle-visibility="toggleVisibility"
/>
```

v-for="fileType in fileTypes" 表示遍历 fileTypes 数组，对于数组中的每个元素，都创建一个新的 TypesComponent 组件，并将数组元素的值赋给局部变量 fileType。

然后，:fileType="fileType" 将这个局部变量 fileType 的值传递给 TypesComponent 组件的 fileType 属性。

所以，尽管父组件并没有 fileType 这个数据属性，但是它仍然可以将 fileType 的值传递给子组件，因为 fileType 是在 v-for 指令中定义的一个局部变量。

这段代码是在父组件中使用 `TypesComponent` 组件的示例，它会根据 `fileTypes` 数组中的文件类型动态地渲染多个 `TypesComponent` 子组件。让我逐步解释其中的内容：

1. `v-for="fileType in fileTypes"`:
   这是 Vue 中用于列表渲染的指令。它会遍历 `fileTypes` 数组中的每一个元素，并为每个元素渲染一个 `TypesComponent` 组件。

2. `:key="fileType"`:
   这是为了给每个渲染的 `TypesComponent` 设置一个唯一的标识符。在这里，我们使用 `fileType` 作为每个子组件的唯一标识符，确保 Vue 在更新列表时能够正确识别每个组件。

3. `:fileType="fileType"`:
   这是将数据从父组件传递给子组件的语法，其中 `fileType` 是父组件中的一个变量，它的值会被传递给 `TypesComponent` 子组件的 `fileType` 属性。这样，子组件就可以使用父组件中的 `fileType` 数据了。

4. `:visibleFileTypes="visibleFileTypes"`:
   同样是将数据从父组件传递给子组件的语法。`visibleFileTypes` 是父组件中的一个变量，它的值会被传递给 `TypesComponent` 子组件的 `visibleFileTypes` 属性。

5. `:files="files"`:
   这也是将数据从父组件传递给子组件的语法。`files` 是父组件中的一个变量，它的值会被传递给 `TypesComponent` 子组件的 `files` 属性。

6. `@toggle-visibility="toggleVisibility"`:
   这是在父组件中监听 `TypesComponent` 子组件触发的 `toggle-visibility` 事件，并在父组件中调用 `toggleVisibility` 方法的语法。这样，父组件就能够响应子组件的行为，并进行相应的处理。

```javascript
props: {
    fileType: {
      type: String,
      required: true,
    },
    visibleFileTypes: {
      type: Array,
      required: true,
    },
    files: {
      type: Array,
      required: true,
    },
  },
```

这种写法是在 Vue 中定义组件的 props，它指定了子组件所期望接收的属性的类型和必要性。让我来解释一下这个写法的意义：

1. `fileType: { type: String, required: true }`:
   这表示 `fileType` 是子组件期望接收的一个属性，它的类型是字符串 (`String`)，并且是必须的 (`required: true`)。这意味着父组件在使用 `TypesComponent` 组件时，必须为 `fileType` 属性提供一个字符串类型的值，否则 Vue 会发出警告。

2. `visibleFileTypes: { type: Array, required: true }`:
   类似地，这表示 `visibleFileTypes` 是子组件期望接收的另一个属性，它的类型是数组 (`Array`)，并且也是必须的。父组件在使用 `TypesComponent` 组件时，必须为 `visibleFileTypes` 属性提供一个数组类型的值，否则 Vue 会发出警告。

3. `files: { type: Array, required: true }`:
   同样的，这表示 `files` 是子组件期望接收的另一个属性，它的类型是数组，并且也是必须的。父组件在使用 `TypesComponent` 组件时，必须为 `files` 属性提供一个数组类型的值，否则 Vue 会发出警告。

这种写法的目的是为了提高代码的可读性和可维护性。通过明确指定每个属性的类型和必要性，我们可以确保组件在使用时得到正确的数据，并且能够更早地发现潜在的问题。Vue 会在开发模式下对传递给 props 的数据进行类型检查，从而帮助我们更容易地识别潜在的错误。

## v-for / v-if

当在 Vue 模板中使用 `v-for` 和 `v-if` 时，它们都是 Vue 提供的指令，用于控制模板中的渲染逻辑。

1. **v-for**：

   - `v-for` 指令用于遍历数组或对象，并将每个元素或属性渲染成相应的 DOM 元素。
   - 语法：`v-for="item in items"`，其中 `items` 是要遍历的数组，`item` 是当前迭代的元素。
   - 示例：
     ```html
     <ul>
       <li v-for="item in items" :key="item.id">{{ item.name }}</li>
     </ul>
     ```
   - 在上面的示例中，`v-for` 遍历 `items` 数组中的每个元素，并将每个元素渲染成一个列表项 `<li>`，同时通过 `:key` 指定了每个列表项的唯一标识符，以便 Vue 可以更高效地管理列表的更新。

2. **v-if**：
   - `v-if` 指令用于根据条件来添加或移除 DOM 元素。
   - 语法：`v-if="condition"`，其中 `condition` 是一个 JavaScript 表达式，如果为 `true`，则渲染元素；如果为 `false`，则不渲染。
   - 示例：
     ```html
     <div v-if="isVisible">This is visible</div>
     ```
   - 在上面的示例中，如果 `isVisible` 为 `true`，则显示 `<div>` 元素中的文本；如果 `isVisible` 为 `false`，则不显示该元素。

在实际应用中，`v-for` 和 `v-if` 往往会结合使用，以根据特定条件渲染列表中的元素。例如，可以在 `v-for` 循环中嵌套 `v-if` 条件，根据每个元素的特定属性来决定是否渲染该元素。

## omponents: {}

## mounted() {}

## computed: {}

## data() {}

## beforeUnmount() {}

## methods: {}

components: 这个选项用于声明该组件内部可以使用的子组件。在你的代码中，TypesComponent 和 AlertComponent 被声明为子组件，这意味着你可以在该组件的模板中使用 <TypesComponent /> 和 <AlertComponent />。

mounted: 这个选项是一个生命周期钩子，它会在组件被挂载到 DOM 后立即调用。在你的代码中，mounted 钩子用于监听 file-uploaded 和 one-file-deleted 事件，当这些事件触发时，会调用 fetchFiles 方法。

computed: 这个选项用于声明计算属性。计算属性是基于组件的响应式依赖进行缓存的。只有在它的相关依赖发生改变时才会重新求值。在你的代码中，firstFileOwner，fileAllCount 和 fileTypes 是计算属性。

data: 这个选项返回一个对象，该对象是组件的响应式数据源。在你的代码中，files 和 visibleFileTypes 是响应式数据。

beforeUnmount: 这个选项是一个生命周期钩子，它会在组件被卸载前立即调用。在你的代码中，beforeUnmount 钩子用于取消监听 file-uploaded 事件。

methods: 这个选项用于声明方法。这些方法将被混入到该组件的 Vue 实例中。你可以通过 this.methodName 来调用这些方法。在你的代码中，collapseAll，expandAll，toggleVisibility，fetchFiles，confirmDeleteAllFiles 和 deleteAllFiles 是方法。


## data 和 computed 的区别

data 和 computed 在 Vue.js 中都是用来声明和管理组件状态的，但它们的使用场景和工作方式有所不同。

data: data 选项是一个函数，返回一个对象，该对象包含了该组件的响应式数据。这些数据是组件的状态，可以在组件的模板和方法中通过 this 访问。当这些数据改变时，Vue.js 会自动更新 DOM。例如：

```javascript
data() {
  return {
    count: 0
  };
},
methods: {
  increment() {
    this.count++;
  }
}
```
在这个例子中，count 是一个响应式数据，当你调用 increment 方法时，count 的值会增加，Vue.js 会自动更新 DOM。

computed: computed 选项用于声明计算属性。计算属性是基于组件的响应式依赖进行缓存的。只有在它的相关依赖发生改变时才会重新求值。这使得计算属性在处理复杂逻辑或者大量计算时更加高效。例如：

```javascript
data() {
  return {
    count: 0
  };
},
computed: {
  doubleCount() {
    return this.count * 2;
  }
}
```
在这个例子中，doubleCount 是一个计算属性，它的值是 count 的两倍。当 count 的值改变时，doubleCount 的值会自动更新。但是，如果 count 的值没有改变，doubleCount 的值会被缓存，不会重新计算。

总的来说，data 用于声明组件的状态，computed 用于声明基于状态的计算属性。你应该根据你的需求选择使用它们。