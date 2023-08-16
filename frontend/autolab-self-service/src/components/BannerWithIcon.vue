<template>
  <div class="row wrap container theme" :class="theme">
    <q-icon v-if="icon !== ''" class="q-mr-lg icon" :name="icon" :size="iconSize"/>
    <div class="col-grow items-center slot-wrapper">
      <slot/>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  icon: {
    type: String,
    default: "",
  },
  iconSize: {
    type: String,
    default: "50px",
  },
  theme: {
    type: String,
    default: "default",
  },
})
</script>

<style scoped lang="scss">
@import 'src/css/quasar.variables.scss';


:deep(.slot-wrapper *) {
  // Remove margin from all children of the slot
  margin: 0;
}

.theme {
  border-radius: 4px;
  padding: 16px;

  &.default {
    // Default is useful for general information messages
    border: 1px solid $primary;

    > .icon {
      color: $primary;
    }
  }

  &.error {
    background-color: #ffebee;
    border: 1px solid #83000d;

    > .icon {
      color: #83000d;
    }
  }

}


</style>
