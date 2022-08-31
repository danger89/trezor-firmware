use crate::ui::{
    constant, display,
    model_tt::theme::{BLACK, ICON_TREZOR_EMPTY, ICON_TREZOR_FULL, WHITE},
};

#[cfg(feature = "sdcard")]
use crate::ui::{
    component::{text::paragraphs::Paragraphs, PageMsg},
    layout::native::RustLayout,
    model_tt::{
        component::{Button, CancelConfirmMsg, Frame, SwipePage},
        theme,
    },
};

#[cfg(all(feature = "sdcard", not(feature = "sdcard_hotswap")))]
use crate::ui::{component::base::ComponentExt, model_tt::component::ButtonMsg};

#[cfg(all(feature = "sdcard", not(feature = "sdcard_hotswap")))]
use crate::ui::model_tt::component::IconDialog;

#[cfg(all(feature = "sdcard", feature = "sdcard_hotswap"))]
pub fn insert_sd_card() -> bool {
    let paragraphs = {
        let mut paragraphs = Paragraphs::new();
        paragraphs = paragraphs
            .add(theme::TEXT_BOLD, "SD card required.")
            .add(theme::TEXT_NORMAL, "Please insert your SD card.");
        paragraphs
    };

    let buttons = Button::cancel_confirm_text(Some("Abort"), "Retry");
    let mut layout = RustLayout::new(Frame::new(
        "SD card protection",
        SwipePage::new(paragraphs, buttons, theme::BG),
    ));
    let res = layout.process();

    !matches!(res, PageMsg::Controls(CancelConfirmMsg::Cancelled))
}

#[cfg(all(feature = "sdcard", not(feature = "sdcard_hotswap")))]
pub fn insert_sd_card() -> bool {
    let mut dialog = RustLayout::new(
        IconDialog::new(
            theme::IMAGE_ERROR,
            "Please unplug the device and insert your SD card.",
            theme::button_bar(
                Button::with_text("CLOSE")
                    .styled(theme::button_default())
                    .map(|msg| {
                        (matches!(msg, ButtonMsg::Clicked)).then(|| CancelConfirmMsg::Confirmed)
                    }),
            ),
        )
        .with_description("SD card required."),
    );

    dialog.process();

    false
}

#[cfg(all(feature = "sdcard", feature = "sdcard_hotswap"))]
pub fn retry_wrong_card() -> bool {
    let paragraphs = {
        let mut paragraphs = Paragraphs::new();
        paragraphs = paragraphs
            .add(theme::TEXT_BOLD, "Wrong SD card.")
            .add(theme::TEXT_NORMAL, "Please retry your SD card.");
        paragraphs
    };

    let buttons = Button::cancel_confirm_text(Some("Abort"), "Retry");
    let mut layout = RustLayout::new(Frame::new(
        "SD card protection",
        SwipePage::new(paragraphs, buttons, theme::BG),
    ));

    let res = layout.process();

    !matches!(res, PageMsg::Controls(CancelConfirmMsg::Cancelled))
}

#[cfg(all(feature = "sdcard", not(feature = "sdcard_hotswap")))]
pub fn retry_wrong_card() -> bool {
    let mut dialog = RustLayout::new(
        IconDialog::new(
            theme::IMAGE_ERROR,
            "Please unplug the device and insert the correct SD card.",
            theme::button_bar(
                Button::with_text("CLOSE")
                    .styled(theme::button_default())
                    .map(|msg| {
                        (matches!(msg, ButtonMsg::Clicked)).then(|| CancelConfirmMsg::Confirmed)
                    }),
            ),
        )
        .with_description("Wrong SD card."),
    );

    dialog.process();

    false
}

#[cfg(feature = "sdcard")]
pub fn retry_sd_card() -> bool {
    let paragraphs = {
        let mut paragraphs = Paragraphs::new();
        paragraphs = paragraphs
            .add(theme::TEXT_BOLD, "SD card fail.")
            .add(theme::TEXT_NORMAL, "Please retry your SD card.");
        paragraphs
    };

    let buttons = Button::cancel_confirm_text(Some("Abort"), "Retry");
    let mut layout = RustLayout::new(Frame::new(
        "SD card protection",
        SwipePage::new(paragraphs, buttons, theme::BG),
    ));
    let res = layout.process();

    !matches!(res, PageMsg::Controls(CancelConfirmMsg::Cancelled))
}

pub fn boot_empty() {
    display::icon(constant::screen().center(), ICON_TREZOR_EMPTY, WHITE, BLACK);
}

pub fn boot_full() {
    display::icon(constant::screen().center(), ICON_TREZOR_FULL, WHITE, BLACK);
}
