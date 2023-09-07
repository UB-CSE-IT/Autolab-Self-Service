<template>
  <tr>
    <td>{{ props.modelValue.name }}</td>
    <td>
      <q-input v-model="startTime"/>
    </td>
    <td>
      <q-input v-model="endTime"/>
    </td>
    <td>
      <q-input v-model="days"/>
    </td>
  </tr>
</template>

<script setup lang="ts">

import {CourseSection} from 'src/types/CourseSectionsTypes'
import {computed, PropType, ref} from 'vue'

const props = defineProps({
  modelValue: {
    type: Object as PropType<CourseSection>,
    required: true,
  },
})

const emits = defineEmits(['update:modelValue'])

const localSection = ref(props.modelValue)

const startTime = computed({
  get: () => props.modelValue?.start_time,
  set: (value: string) => {
    localSection.value.start_time = value
    emits('update:modelValue', localSection.value)
  },
})

const endTime = computed({
  get: () => props.modelValue?.end_time,
  set: (value: string) => {
    localSection.value.end_time = value
    emits('update:modelValue', localSection.value)
  },
})

const days = computed({
  get: () => props.modelValue?.days_code,
  set: (value: number) => {
    localSection.value.days_code = value
    emits('update:modelValue', localSection.value)
  },
})


</script>

<style scoped lang="scss">

</style>
