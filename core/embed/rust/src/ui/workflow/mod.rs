pub mod boot;

use crate::ui::{
    model::screens::{boot_empty, boot_full},
    workflow::boot::boot_workflow,
};

#[no_mangle]
pub extern "C" fn boot_screen_empty() {
    boot_empty();
}

#[no_mangle]
pub extern "C" fn boot_screen_full() {
    boot_full();
}

#[no_mangle]
pub extern "C" fn boot_firmware() {
    boot_workflow();
}
