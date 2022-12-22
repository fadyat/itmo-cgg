## Computer geometry and graphics

Here you can find some problems and solutions for Computer Geometry and Graphics course.

We use `Python` and `PyQT` for the GUI.

> As advice to you, better use `C++` with `Qt` for the GUI, because it is much faster and more convenient.
>
> You may think: "ooohhh, man, idk `C++`". But trust me, it will be easier too you.
>
> If you still want Python, try to use `numpy` and minimize `for` loops in your code.

Please don't look this code, it is very bad, actually PNG and anti-aliasing.

Another part works normal, but slow.

All problems you can find [here](./docs/problems.pdf).

If you want to use some pictures, you can find them [here](./docs/images).

### Which parts are done?

- [x] PNM format support
- [x] Color spaces
- [x] Gamma correction
- [x] Drawing bitmap lines with anti-aliasing applied
> Work so bad
- [x] Pseudo-tinting of images, Dithering
> Have a mistake in the 8x8 ordered dithering
- [x] Image scaling
> - Implemented only 3/4 algorithms
> - Shift works only in integer coordinates
- [x] PNG format support
> Works like a separate widget, not like a part of the program
- [ ] JPEG format support
- [ ] Image histogram
- [ ] Image filtering
