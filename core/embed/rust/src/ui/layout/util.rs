use crate::{
    error::Error,
    micropython::{
        buffer::{get_buffer, obj_as_str},
        iter::{Iter, IterBuf},
        obj::Obj,
    },
    ui::component::text::paragraphs::{Paragraph, ParagraphSource, VecExt},
};
use core::str;
use cstr_core::cstr;
use heapless::Vec;

pub fn iter_into_objs<const N: usize>(iterable: Obj) -> Result<[Obj; N], Error> {
    let err = Error::ValueError(cstr!("Invalid iterable length"));
    let mut vec = Vec::<Obj, N>::new();
    let mut iter_buf = IterBuf::new();
    for item in Iter::try_from_obj_with_buf(iterable, &mut iter_buf)? {
        vec.push(item).map_err(|_| err)?;
    }
    // Returns error if array.len() != N
    vec.into_array().map_err(|_| err)
}

pub fn iter_into_array<T, const N: usize>(iterable: Obj) -> Result<[T; N], Error>
where
    T: TryFrom<Obj, Error = Error>,
{
    let err = Error::ValueError(cstr!("Invalid iterable length"));
    let mut vec = Vec::<T, N>::new();
    let mut iter_buf = IterBuf::new();
    for item in Iter::try_from_obj_with_buf(iterable, &mut iter_buf)? {
        vec.push(item.try_into()?).map_err(|_| err)?;
    }
    // Returns error if array.len() != N
    vec.into_array().map_err(|_| err)
}

fn objslice_at<'a>(
    objslice: &'a [Paragraph<Obj>],
    index: usize,
    offset: usize,
    buffer: &'a mut [u8],
) -> Paragraph<&'a str> {
    const HEX_LOWER: [u8; 16] = *b"0123456789abcdef";
    let par = &objslice[index];
    let content: &Obj = par.content();

    // Handle None as empty string.
    if *content == Obj::const_none() {
        return par.with_content("");
    }

    // Handle str.
    if content.is_type_str() || content.is_qstr() {
        return match obj_as_str(content) {
            Ok(s) => par.with_content(&s[offset..]),
            Err(_) => par.with_content("ERROR"),
        };
    }

    // Handling bytes from now on.
    if !content.is_type_bytes() {
        return par.with_content("ERROR");
    }

    // Convert offset to byte representation, handle case where it points in the
    // middle of a byte.
    let bin_off = offset / 2;
    let hex_off = offset % 2;

    // SAFETY:
    // (a) only immutable references are taken
    // (b) reference is discarded before returning to micropython
    let bin_slice = if let Ok(buf) = unsafe { get_buffer(*content) } {
        &buf[bin_off..]
    } else {
        return par.with_content("ERROR");
    };
    let mut i: usize = 0;
    for b in bin_slice.iter().take(buffer.len() / 2) {
        let hi: usize = ((b & 0xf0) >> 4).into();
        let lo: usize = (b & 0x0f).into();
        buffer[i] = HEX_LOWER[hi];
        buffer[i + 1] = HEX_LOWER[lo];
        i += 2;
    }

    // SAFETY: only <0x7f bytes are used to construct the string
    let result = unsafe { str::from_utf8_unchecked(&buffer[0..i]) };
    par.with_content(&result[hex_off..])
}

impl<const N: usize> ParagraphSource for [Paragraph<Obj>; N] {
    fn at<'a>(&'a self, index: usize, offset: usize, buffer: &'a mut [u8]) -> Paragraph<&'a str> {
        objslice_at(self.as_slice(), index, offset, buffer)
    }

    fn size(&self) -> usize {
        N
    }
}

impl<const N: usize> ParagraphSource for Vec<Paragraph<Obj>, N> {
    fn at<'a>(&'a self, index: usize, offset: usize, buffer: &'a mut [u8]) -> Paragraph<&'a str> {
        objslice_at(self, index, offset, buffer)
    }

    fn size(&self) -> usize {
        self.len()
    }
}

impl<const N: usize> VecExt<Obj> for Vec<Paragraph<Obj>, N> {
    fn add(&mut self, paragraph: Paragraph<Obj>) -> &mut Self {
        if *paragraph.content() == Obj::const_none() {
            return self;
        }
        if self.push(paragraph).is_err() {
            #[cfg(feature = "ui_debug")]
            panic!("paragraph list is full");
        }
        self
    }
}
