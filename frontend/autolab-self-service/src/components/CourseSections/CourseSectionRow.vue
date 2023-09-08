<template>
  <tr :class="{'bg-yellow-2': localSection?.updated}">
    <td>{{ props.modelValue.name }}</td>
    <td>
      <q-input v-model="startTime"/>
    </td>
    <td>
      <q-input v-model="endTime"/>
    </td>
    <td>
      <q-input v-model.number="days"/>
    </td>
    <td>
      <span v-if="localSection.updated" class="text-red">Not saved</span>
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

const localSection = ref<CourseSection>(props.modelValue)

const startTime = computed({
  get: () => props.modelValue?.start_time,
  set: (value: string) => {
    localSection.value.start_time = value
    localSection.value.updated = true
    emits('update:modelValue', localSection.value)
  },
})

const endTime = computed({
  get: () => props.modelValue?.end_time,
  set: (value: string) => {
    localSection.value.end_time = value
    localSection.value.updated = true
    emits('update:modelValue', localSection.value)
  },
})

const days = computed({
  get: () => props.modelValue?.days_code,
  set: (value: number) => {
    localSection.value.days_code = value
    localSection.value.updated = true
    emits('update:modelValue', localSection.value)
  },
})


</script>

<style scoped lang="scss">

</style>
