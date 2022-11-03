use heapless::Vec;

use crate::ui::{
    component::{Component, Event, EventCtx, Never, Paginate},
    display,
    geometry::{Alignment, Insets, LinearPlacement, Offset, Point, Rect},
};

use super::layout::{LayoutFit, TextLayout, TextStyle};

/// Used as an upper bound of number of different styles we may render on single
/// page.
pub const MAX_LINES: usize = 10;
/// Maximum space between paragraphs. Actual result may be smaller (even 0) if
/// it would make paragraphs overflow the bounding box.
pub const DEFAULT_SPACING: i16 = 0;
/// Offset of paragraph text from the top of the paragraph bounding box. Tweak
/// these values to get nice alignment of baselines relative to the surrounding
/// components.
pub const PARAGRAPH_TOP_SPACE: i16 = -1;
/// Offset of paragraph bounding box bottom relative to bottom of its text.
pub const PARAGRAPH_BOTTOM_SPACE: i16 = 5;

pub type ParagraphVecLong<T> = Vec<Paragraph<T>, 32>;
pub type ParagraphVecShort<T> = Vec<Paragraph<T>, 8>;

pub trait ParagraphSource {
    fn at(&self, i: usize) -> Paragraph<&str>;
    fn size(&self) -> usize;

    fn into_paragraphs(self) -> Paragraphs<Self>
    where
        Self: Sized,
    {
        Paragraphs::new(self)
    }
}

impl<T, const N: usize> ParagraphSource for Vec<Paragraph<T>, N>
where
    T: AsRef<str>,
{
    fn at(&self, i: usize) -> Paragraph<&str> {
        self[i].to_ref()
    }

    fn size(&self) -> usize {
        self.len()
    }
}

impl<T, const N: usize> ParagraphSource for [Paragraph<T>; N]
where
    T: AsRef<str>,
{
    fn at(&self, i: usize) -> Paragraph<&str> {
        self[i].to_ref()
    }

    fn size(&self) -> usize {
        self.len()
    }
}

impl<T> ParagraphSource for Paragraph<T>
where
    T: AsRef<str>,
{
    fn at(&self, i: usize) -> Paragraph<&str> {
        assert_eq!(i, 0);
        self.to_ref()
    }

    fn size(&self) -> usize {
        1
    }
}

pub struct Paragraphs<T> {
    area: Rect,
    placement: LinearPlacement,
    offset: PageOffset,
    visible: Vec<TextLayout, MAX_LINES>,
    source: T,
}

impl<T> Paragraphs<T>
where
    T: ParagraphSource,
{
    pub fn new(source: T) -> Self {
        Self {
            area: Rect::zero(),
            placement: LinearPlacement::vertical()
                .align_at_center()
                .with_spacing(DEFAULT_SPACING),
            offset: PageOffset::default(),
            visible: Vec::new(),
            source,
        }
    }

    pub fn with_placement(mut self, placement: LinearPlacement) -> Self {
        self.placement = placement;
        self
    }

    pub fn with_spacing(mut self, spacing: i16) -> Self {
        self.placement = self.placement.with_spacing(spacing);
        self
    }

    pub fn inner(&self) -> &T {
        &self.source
    }

    pub fn inner_mut(&mut self) -> &mut T {
        &mut self.source
    }

    /// Update bounding boxes of paragraphs on the current page. First determine
    /// the number of visible paragraphs and their sizes. These are then
    /// arranged according to the layout.
    fn change_offset(&mut self, offset: PageOffset) {
        self.offset = offset;
        Self::dyn_change_offset(self.area, offset, &self.source, self.visible.as_mut());
        self.placement.arrange(self.area, &mut self.visible);
    }

    /// Helper for `change_offset` which should not get monomorphized as it
    /// doesn't refer to T or Self.
    fn dyn_change_offset(
        mut area: Rect,
        mut offset: PageOffset,
        source: &dyn ParagraphSource,
        visible: &mut Vec<TextLayout, MAX_LINES>,
    ) {
        visible.clear();
        let full_height = area.height();

        while offset.par < source.size() {
            let (next_offset, remaining_area, layout) = offset.advance(area, source, full_height);
            if let Some(layout) = layout {
                unwrap!(visible.push(layout));
            }
            if let Some(remaining_area) = remaining_area {
                #[cfg(feature = "ui_debug")]
                assert_eq!(next_offset.par, offset.par + 1);
                area = remaining_area;
                offset = next_offset;
            } else {
                break;
            }
        }
    }

    fn break_pages(&self) -> PageBreakIterator<T> {
        PageBreakIterator {
            paragraphs: self,
            current: None,
        }
    }

    /// Returns iterator over visible layouts (bounding box, style) together
    /// with corresponding string content. Should not get monomorphized.
    fn visible_content<'a>(
        content: &'a dyn ParagraphSource,
        visible: &'a [TextLayout],
        offset: PageOffset,
    ) -> impl Iterator<Item = (&'a TextLayout, &'a str)> {
        visible.iter().zip(
            (offset.par..content.size())
                .map(|i| content.at(i))
                .filter(|p| !p.content.is_empty())
                .enumerate()
                .map(move |(i, p): (usize, Paragraph<&str>)| {
                    if i == 0 {
                        &p.content[offset.chr..]
                    } else {
                        p.content
                    }
                }),
        )
    }
}

impl<T> Component for Paragraphs<T>
where
    T: ParagraphSource,
{
    type Msg = Never;

    fn place(&mut self, bounds: Rect) -> Rect {
        self.area = bounds;
        self.change_offset(self.offset);
        self.area
    }

    fn event(&mut self, _ctx: &mut EventCtx, _event: Event) -> Option<Self::Msg> {
        None
    }

    fn paint(&mut self) {
        for (layout, content) in Self::visible_content(&self.source, &self.visible, self.offset) {
            layout.render_text(content);
        }
    }

    fn bounds(&self, sink: &mut dyn FnMut(Rect)) {
        sink(self.area);
        for layout in &self.visible {
            sink(layout.bounds)
        }
    }
}

impl<T> Paginate for Paragraphs<T>
where
    T: ParagraphSource,
{
    fn page_count(&mut self) -> usize {
        // There's always at least one page.
        self.break_pages().count().max(1)
    }

    fn change_page(&mut self, to_page: usize) {
        if let Some(offset) = self.break_pages().nth(to_page) {
            self.change_offset(offset)
        } else {
            // Should not happen, set index to first paragraph and render empty page.
            self.offset = PageOffset::default();
            self.visible.clear()
        }
    }
}

#[cfg(feature = "ui_debug")]
pub mod trace {
    use crate::ui::component::text::layout::trace::TraceSink;

    use super::*;

    impl<T: ParagraphSource> crate::trace::Trace for Paragraphs<T> {
        fn trace(&self, t: &mut dyn crate::trace::Tracer) {
            t.open("Paragraphs");
            for (layout, content) in Self::visible_content(&self.source, &self.visible, self.offset)
            {
                layout.layout_text(content, &mut layout.initial_cursor(), &mut TraceSink(t));
                t.string("\n");
            }
            t.close();
        }
    }
}

#[derive(Clone, Copy)]
pub struct Paragraph<T> {
    /// Paragraph text.
    content: T,
    /// Paragraph style.
    style: &'static TextStyle,
    /// Paragraph alignment.
    align: Alignment,
    /// Place next paragraph on new page.
    break_after: bool,
    /// Try to keep this and the next paragraph on the same page. NOTE: doesn't
    /// work if two or more subsequent paragraphs have this flag.
    no_break: bool,
}

impl<T> Paragraph<T> {
    pub const fn new(style: &'static TextStyle, content: T) -> Self {
        Self {
            content,
            style,
            align: Alignment::Start,
            break_after: false,
            no_break: false,
        }
    }

    pub const fn centered(mut self) -> Self {
        self.align = Alignment::Center;
        self
    }

    pub const fn break_after(mut self) -> Self {
        self.break_after = true;
        self
    }

    pub const fn no_break(mut self) -> Self {
        self.no_break = true;
        self
    }

    pub fn content(&self) -> &T {
        &self.content
    }

    pub fn update(&mut self, content: T) {
        self.content = content
    }

    fn to_ref(&self) -> Paragraph<&str>
    where
        T: AsRef<str>,
    {
        Paragraph {
            content: self.content.as_ref(),
            style: self.style,
            align: self.align,
            break_after: self.break_after,
            no_break: self.no_break,
        }
    }

    fn layout(&self, area: Rect) -> TextLayout {
        TextLayout {
            padding_top: PARAGRAPH_TOP_SPACE,
            padding_bottom: PARAGRAPH_BOTTOM_SPACE,
            ..TextLayout::new(*self.style)
                .with_align(self.align)
                .with_bounds(area)
        }
    }
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
struct PageOffset {
    /// Index of paragraph.
    par: usize,

    /// Index of character in the paragraph.
    chr: usize,
}

impl PageOffset {
    /// Given an `PageOffset` and a `Rect` area, returns:
    ///
    /// - The next offset.
    /// - Part of `area` that remains free after the current offset is rendered
    ///   into it, or `None` if we've reached the end of the page.
    /// - The `TextLayout` for the current offset, or `None` if `area` is too
    ///   small to render any text.
    ///
    /// If the returned remaining area is not None then it holds that
    /// `next_offset.par == self.par + 1`.
    fn advance(
        mut self,
        area: Rect,
        source: &dyn ParagraphSource,
        full_height: i16,
    ) -> (PageOffset, Option<Rect>, Option<TextLayout>) {
        let paragraph = source.at(self.par);

        // Skip empty paragraphs.
        if paragraph.content.is_empty() {
            self.par += 1;
            self.chr = 0;
            return (self, Some(area), None);
        }

        // Handle the `no_break` flag used to keep key-value pair on the same page.
        if paragraph.no_break && self.chr == 0 {
            if let Some(next_paragraph) =
                (self.par + 1 < source.size()).then(|| source.at(self.par + 1))
            {
                if Self::should_place_pair_on_next_page(
                    &paragraph,
                    &next_paragraph,
                    area,
                    full_height,
                ) {
                    return (self, None, None);
                }
            }
        }

        // Find out the dimensions of the paragraph at given char offset.
        let mut layout = paragraph.layout(area);
        let fit = layout.fit_text(&paragraph.content[self.chr..]);
        let (used, remaining_area) = area.split_top(fit.height());
        layout.bounds = used;

        let page_full: bool;
        match fit {
            LayoutFit::Fitting { .. } => {
                // Continue with start of next paragraph.
                self.par += 1;
                self.chr = 0;
                // Handle hard break if requested for this paragraph.
                page_full = paragraph.break_after;
            }
            LayoutFit::OutOfBounds {
                processed_chars, ..
            } => {
                // Reached end of the page and not all content fits.
                self.chr += processed_chars;
                // Do not render more paragraphs.
                page_full = true;
            }
        }

        (
            self,
            Some(remaining_area).filter(|_| !page_full),
            Some(layout).filter(|_| fit.height() > 0),
        )
    }

    fn should_place_pair_on_next_page(
        this_paragraph: &Paragraph<&str>,
        next_paragraph: &Paragraph<&str>,
        area: Rect,
        full_height: i16,
    ) -> bool {
        // Never break if we're at the beginning of the page.
        let remaining_height = area.height();
        if remaining_height >= full_height {
            return false;
        }

        let full_area = area.with_height(full_height);
        let key_height = this_paragraph
            .layout(full_area)
            .fit_text(this_paragraph.content)
            .height();
        let val_height = next_paragraph
            .layout(full_area)
            .fit_text(next_paragraph.content)
            .height();
        let screen_full_threshold = this_paragraph.style.text_font.line_height()
            + next_paragraph.style.text_font.line_height();

        if key_height + val_height > remaining_height {
            return
                // There are only ~2 remaining lines, don't try to fit and put everything on the
                // next page.
                (remaining_height <= screen_full_threshold)
                // More than 2 remaining lines so try to fit something -- but won't
                // fit at least one line of value.
                || (val_height > 0 && key_height > remaining_height)
                // Whole property won't fit to the page, but it will fit on a page
                // by itself.
                || (key_height + val_height <= full_height);
        }

        // None of the above, continue fitting on the same page.
        false
    }
}

struct PageBreakIterator<'a, T> {
    /// Reference to paragraph vector.
    paragraphs: &'a Paragraphs<T>,

    /// Current offset, or `None` before first `next()` call.
    current: Option<PageOffset>,
}

impl<T: ParagraphSource> PageBreakIterator<'_, T> {
    fn dyn_next(
        mut area: Rect,
        paragraphs: &dyn ParagraphSource,
        mut offset: PageOffset,
    ) -> Option<PageOffset> {
        let full_height = area.height();

        while offset.par < paragraphs.size() {
            let (next_offset, remaining_area, _layout) =
                offset.advance(area, paragraphs, full_height);
            if next_offset.par >= paragraphs.size() {
                // Last page.
                return None;
            } else if let Some(remaining_area) = remaining_area {
                #[cfg(feature = "ui_debug")]
                assert_eq!(next_offset.par, offset.par + 1);
                area = remaining_area;
                offset = next_offset;
            } else {
                return Some(next_offset);
            }
        }

        None
    }
}

/// Yields indices to beginnings of successive pages. First value is always
/// `PageOffset { 0, 0 }` even if the paragraph vector is empty.
impl<T: ParagraphSource> Iterator for PageBreakIterator<'_, T> {
    /// `PageOffset` denotes the first paragraph that is rendered and a
    /// character offset in that paragraph.
    type Item = PageOffset;

    fn next(&mut self) -> Option<Self::Item> {
        let first = self.current.is_none();
        let current = self.current.get_or_insert_with(PageOffset::default);
        if first {
            return self.current;
        }

        let next = Self::dyn_next(self.paragraphs.area, &self.paragraphs.source, *current);
        if next.is_some() {
            // Better panic than infinite loop.
            assert_ne!(next, self.current);
            self.current = next;
        }
        next
    }
}

pub struct Checklist<T> {
    area: Rect,
    paragraphs: Paragraphs<T>,
    current: usize,
    icon_current: &'static [u8],
    icon_done: &'static [u8],
}

impl<T> Checklist<T> {
    const CHECK_WIDTH: i16 = 16;
    const DONE_OFFSET: Offset = Offset::new(-2, 6);
    const CURRENT_OFFSET: Offset = Offset::new(2, 3);

    pub fn from_paragraphs(
        icon_current: &'static [u8],
        icon_done: &'static [u8],
        current: usize,
        paragraphs: Paragraphs<T>,
    ) -> Self {
        Self {
            area: Rect::zero(),
            paragraphs,
            current,
            icon_current,
            icon_done,
        }
    }

    fn paint_icon(&self, layout: &TextLayout, icon: &'static [u8], offset: Offset) {
        let top_left = Point::new(self.area.x0, layout.bounds.y0);
        display::icon_top_left(
            top_left + offset,
            icon,
            layout.style.text_color,
            layout.style.background_color,
        );
    }
}

impl<T> Component for Checklist<T>
where
    T: ParagraphSource,
{
    type Msg = Never;

    fn place(&mut self, bounds: Rect) -> Rect {
        self.area = bounds;
        let para_area = bounds.inset(Insets::left(Self::CHECK_WIDTH));
        self.paragraphs.place(para_area);
        self.area
    }

    fn event(&mut self, ctx: &mut EventCtx, event: Event) -> Option<Self::Msg> {
        self.paragraphs.event(ctx, event)
    }

    fn paint(&mut self) {
        self.paragraphs.paint();

        let current_visible = self.current.saturating_sub(self.paragraphs.offset.par);
        for layout in self.paragraphs.visible.iter().take(current_visible) {
            self.paint_icon(layout, self.icon_done, Self::DONE_OFFSET);
        }
        if let Some(layout) = self.paragraphs.visible.iter().nth(current_visible) {
            self.paint_icon(layout, self.icon_current, Self::CURRENT_OFFSET);
        }
    }

    fn bounds(&self, sink: &mut dyn FnMut(Rect)) {
        sink(self.area);
        self.paragraphs.bounds(sink);
    }
}

#[cfg(feature = "ui_debug")]
impl<T: ParagraphSource> crate::trace::Trace for Checklist<T> {
    fn trace(&self, t: &mut dyn crate::trace::Tracer) {
        t.open("Checklist");
        t.field("current", &self.current);
        t.field("items", &self.paragraphs);
        t.close();
    }
}

pub trait VecExt<T> {
    fn add(&mut self, paragraph: Paragraph<T>) -> &mut Self;
}

impl<T, const N: usize> VecExt<T> for Vec<Paragraph<T>, N>
where
    T: AsRef<str>,
{
    fn add(&mut self, paragraph: Paragraph<T>) -> &mut Self {
        if paragraph.content.as_ref().is_empty() {
            return self;
        }
        if self.push(paragraph).is_err() {
            #[cfg(feature = "ui_debug")]
            panic!("paragraph list is full");
        }
        self
    }
}
