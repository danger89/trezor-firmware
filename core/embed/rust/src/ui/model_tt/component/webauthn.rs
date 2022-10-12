use crate::ui::{
    component::{Child, Component, Event, EventCtx, Image},
    display::{self, Font},
    geometry::{Insets, Point, Rect},
    model_tt::{
        component::{
            swipe::{Swipe, SwipeDirection},
            theme,
            webauthn_icons::get_webauthn_icon_data,
            ScrollBar,
        },
        constant,
    },
};

use super::CancelConfirmMsg;

const ICON_HEIGHT: i16 = 70;
const SCROLLBAR_INSER_TOP: i16 = 5;
const SCROLLBAR_HEIGHT: i16 = 10;
const TEXT_Y_BASELINES: [i16; 2] = [130, 160];
const TEXT_Y_BASELINES_SCROLLBAR: [i16; 2] = [145, 175];

pub enum FidoMsg {
    Confirmed(usize),
    Cancelled,
}

#[derive(Clone, Copy)]
pub struct FidoPage<T> {
    app_name: T,
    account_name: T,
}

impl<T> FidoPage<T> {
    pub fn new(app_name: T, account_name: T) -> Self {
        Self {
            app_name,
            account_name,
        }
    }
}

pub struct FidoPaginatedPage<F: Fn(usize) -> FidoPage<T>, T, U> {
    page_swipe: Swipe,
    icon: Child<Image>,
    /// Function/closure that will return appropriate page on demand.
    get_page: F,
    scrollbar: ScrollBar,
    content_area: Rect,
    fade: bool,
    controls: U,
}

impl<F, T, U> FidoPaginatedPage<F, T, U>
where
    F: Fn(usize) -> FidoPage<T>,
    T: AsRef<str>,
    U: Component<Msg = CancelConfirmMsg>,
{
    pub fn new(get_page: F, page_count: usize, icon_name: Option<T>, controls: U) -> Self {
        let icon_data = get_webauthn_icon_data(icon_name.as_ref());

        // Preparing scrollbar and setting its page-count.
        let mut scrollbar = ScrollBar::horizontal();
        scrollbar.set_count_and_active_page(page_count, 0);

        // Preparing swipe component and setting possible initial
        // swipe directions according to number of pages.
        let mut page_swipe = Swipe::horizontal();
        page_swipe.allow_right = scrollbar.has_previous_page();
        page_swipe.allow_left = scrollbar.has_next_page();

        Self {
            page_swipe,
            icon: Child::new(Image::new(icon_data)),
            get_page,
            scrollbar,
            content_area: Rect::zero(),
            fade: false,
            controls,
        }
    }

    fn on_page_swipe(&mut self, ctx: &mut EventCtx, swipe: SwipeDirection) {
        // Change the page number.
        match swipe {
            SwipeDirection::Left if self.scrollbar.has_next_page() => {
                self.scrollbar.go_to_next_page();
            }
            SwipeDirection::Right if self.scrollbar.has_previous_page() => {
                self.scrollbar.go_to_previous_page();
            }
            _ => {} // page did not change
        };

        // Disable swipes on the boundaries. Not allowing carousel effect.
        self.page_swipe.allow_right = self.scrollbar.has_previous_page();
        self.page_swipe.allow_left = self.scrollbar.has_next_page();

        // Redraw the page.
        ctx.request_paint();

        // Reset backlight to normal level on next paint.
        self.fade = true;
    }

    fn active_page(&self) -> usize {
        self.scrollbar.active_page
    }
}

impl<F, T, U> Component for FidoPaginatedPage<F, T, U>
where
    F: Fn(usize) -> FidoPage<T>,
    T: AsRef<str>,
    U: Component<Msg = CancelConfirmMsg>,
{
    type Msg = FidoMsg;

    fn place(&mut self, bounds: Rect) -> Rect {
        self.page_swipe.place(bounds);

        // Place the control buttons.
        let controls_area = self.controls.place(bounds);

        // Get the image and content areas.
        let content_area = bounds.inset(Insets::bottom(controls_area.height()));
        let (image_area, content_area) = content_area.split_top(ICON_HEIGHT);
        self.content_area = content_area;

        // In case of showing a scrollbar, getting its area and placing it.
        if self.scrollbar.page_count > 1 {
            let (scrollbar_area, content_area) = content_area
                .inset(Insets::top(SCROLLBAR_INSER_TOP))
                .split_top(SCROLLBAR_HEIGHT);
            self.scrollbar.place(scrollbar_area);
            self.content_area = content_area;
        }

        // Place the icon image.
        self.icon.place(image_area);

        bounds
    }

    fn event(&mut self, ctx: &mut EventCtx, event: Event) -> Option<Self::Msg> {
        if let Some(swipe) = self.page_swipe.event(ctx, event) {
            // Swipe encountered, update the page.
            self.on_page_swipe(ctx, swipe);
        }
        if let Some(msg) = self.controls.event(ctx, event) {
            // Some button was clicked, send results.
            match msg {
                CancelConfirmMsg::Confirmed => return Some(FidoMsg::Confirmed(self.active_page())),
                CancelConfirmMsg::Cancelled => return Some(FidoMsg::Cancelled),
            }
        }
        None
    }

    fn paint(&mut self) {
        self.icon.paint();
        self.controls.paint();

        // Deciding on the vertical position of the text according to
        // having a scrollbar or not. Painting the scrollbar if needed.
        let [app_name_y_baseline, account_name_y_baseline] = if self.scrollbar.page_count > 1 {
            self.scrollbar.paint();
            TEXT_Y_BASELINES_SCROLLBAR
        } else {
            TEXT_Y_BASELINES
        };

        let current_page = (self.get_page)(self.active_page());

        // Erasing the old text content before writing the new one.
        display::rect_fill(self.content_area, theme::BG);

        // App name is always there
        display::text_center(
            Point::new(constant::WIDTH / 2, app_name_y_baseline),
            current_page.app_name.as_ref(),
            Font::BOLD,
            theme::FG,
            theme::BG,
        );

        // Account name is optional.
        if !current_page.account_name.as_ref().is_empty() {
            // Showing it only if it differs from app name.
            // (Dummy requests usually have some text as both app_name and account_name.)
            if current_page.account_name.as_ref() != current_page.app_name.as_ref() {
                display::text_center(
                    Point::new(constant::WIDTH / 2, account_name_y_baseline),
                    current_page.account_name.as_ref(),
                    Font::BOLD,
                    theme::FG,
                    theme::BG,
                );
            }
        }

        if self.fade {
            self.fade = false;
            // Note that this is blocking and takes some time.
            display::fade_backlight(theme::BACKLIGHT_NORMAL);
        }
    }
}

#[cfg(feature = "ui_debug")]
impl<F, T, U> crate::trace::Trace for FidoPaginatedPage<F, T, U>
where
    F: Fn(usize) -> FidoPage<T>,
{
    fn trace(&self, t: &mut dyn crate::trace::Tracer) {
        t.open("FidoPaginatedPage");
        t.close();
    }
}
