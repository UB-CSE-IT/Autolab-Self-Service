<template>
  <q-checkbox v-model="state.checked"
              :disable="state.mostRecentApiDataLoader?.state.loading"
              style="width: 150px"
              @update:modelValue="checkStateChanged">
    <div>
      <span v-if="state.mostRecentApiDataLoader?.state.loading"><q-icon name="upload" class="q-mr-sm"/>Saving...</span>
      <span v-else-if="state.updated">
        <span v-if="state.success" class="text-green"><q-icon name="done" class="q-mr-sm"/>Saved!</span>
          <span v-else class="text-red-10">
            <q-tooltip anchor="top middle" self="center middle">
              {{ state.mostRecentApiDataLoader?.state.error }}
            </q-tooltip>
            <q-icon name="error" class="q-mr-sm"/>
            Error (hover)
          </span>
        </span>
    </div>
  </q-checkbox>
</template>

<script setup lang="ts">

import {PropType, reactive} from 'vue'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'

const emits = defineEmits(['updated', 'error', 'loading', 'update:modelValue'])
// updated(bool): called when the value was successfully updated
//   bool: the new value (true if checked, false if unchecked)
// error(bool, string): called when the value was unsuccessfully updated
//   bool: the attempted new value (true if checked, false if unchecked). The current value will be the opposite.
//   string: the error message
// loading(bool): called when the value is being updated
//   bool: the attempted new value (true if checked, false if unchecked)

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  checkedApiDataLoader: {
    type: Object as PropType<PortalApiDataLoader<any>>,
    required: true,
  },
  uncheckedApiDataLoader: {
    type: PortalApiDataLoader<any>,
    required: true,
  },
})

const state = reactive({
  checked: props.modelValue,
  updated: false,
  success: false,
  mostRecentApiDataLoader: props.modelValue ? props.checkedApiDataLoader : props.uncheckedApiDataLoader as PortalApiDataLoader<any>,
})

function checkStateChanged() {
  if (state.checked) {
    state.mostRecentApiDataLoader = props.checkedApiDataLoader
  } else {
    state.mostRecentApiDataLoader = props.uncheckedApiDataLoader
  }

  emits('loading', state.checked)
  state.mostRecentApiDataLoader.fetch()
      .then(() => {
        state.updated = true
        state.success = !state.mostRecentApiDataLoader.state.error
        if (state.success) {
          emits('updated', state.checked)
          emits('update:modelValue', state.checked)
        } else {
          emits('error', state.checked, state.mostRecentApiDataLoader.state.error)
          state.checked = !state.checked
        }
      })
}

</script>
