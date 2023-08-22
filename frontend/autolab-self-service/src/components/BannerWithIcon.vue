<template>
  <div class="row no-wrap container theme" :class="theme">
    <q-icon v-if="icon !== ''" class="q-mr-lg icon" :name="icon" :size="iconSize"/>
    <div class="items-center slot-wrapper" style="width: 100%">
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


:deep(.slot-wrapper > *) {
  // Remove margin from all children of the slot
  margin: 0;
}

.theme {
  border-radius: 4px;
  padding: 16px;
  margin: 16px 0;
  color: black;

  &.default {
    // Default is useful for general information messages
    background-color: #e3f2fd;
    border: 1px solid $primary;

    > .icon {
      color: $primary;
    }
  }

  &.error {
    background-color: #ffebee;
    border: 1px solid $negative;

    > .icon {
      color: $negative;
    }
  }

  &.warning {
    background-color: #fff3e0;
    border: 1px solid $warning;

    > .icon {
      color: $warning;
    }
  }

  &.success {
    background-color: #e8f5e9;
    border: 1px solid $positive;

    > .icon {
      color: $positive;
    }
  }

  &.debug {
    background-color: $developer-bg;
    border-left: 6px solid $developer;
    border-right: 6px solid $developer;
    border-radius: 16px;

    > .icon {
      color: $developer;
    }
  }

  &.admin {
    background-color: $admin-bg;
    border-left: 6px solid $admin;
    border-right: 6px solid $admin;
    border-radius: 16px;

    > .icon {
      color: $admin;
    }
  }

}


</style>
