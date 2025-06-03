# Changelog

## [0.2.0](https://github.com/jungomi/progrich/compare/v0.1.0...v0.2.0) (2025-06-03)


### Features

* **table:** add a table that displays the rows dynamically ([e8ed6b7](https://github.com/jungomi/progrich/commit/e8ed6b7fd235c875ab123a083f2d4f23c9782ef0))


### Bug Fixes

* **manager:** restore cursor after keyboard interrupts (Ctrl+C) ([d3e1d90](https://github.com/jungomi/progrich/commit/d3e1d906f690baa690c972e586b988e8924a6ad5))
* **signal_handler:** avoid private type that does not exist in 3.12 ([ca01976](https://github.com/jungomi/progrich/commit/ca01976cf57dcb789bbb6d62f29befe63029c0d6))


### Documentation

* show an example of how to use the table ([91d7509](https://github.com/jungomi/progrich/commit/91d75092287cf13633f75f7b915803174415877c))

## 0.1.0 (2025-05-22)


### ⚠ BREAKING CHANGES

* rename project to progrich

### Features

* define Widget to handle any kind of progress widget ([76df27d](https://github.com/jungomi/progrich/commit/76df27d0b127108c1be2a40b732e265d1b4184bb))
* **fmt:** implement formatting of duration ([1f2b3b7](https://github.com/jungomi/progrich/commit/1f2b3b78879159768a6671a47f3c0cacbc215144))
* implement simplified progress bar with better default layout ([b3196e4](https://github.com/jungomi/progrich/commit/b3196e4f6aa386efa9662e6646105b8dc135a2a9))
* **manager:** allow modifying the console and adhere to it ([a332b46](https://github.com/jungomi/progrich/commit/a332b46f0e58d72a4752e3614347c5cf040549f3))
* **manager:** create a manager that handles multiple progress bars ([404f2c4](https://github.com/jungomi/progrich/commit/404f2c4a059cbb4f26d89a0e7a97bc70a27db05b))
* **manager:** provide different display orders (init, start-time, completed-on-top) ([3464f0a](https://github.com/jungomi/progrich/commit/3464f0adefc8e6d742115e3c1f719b1aa923adc7))
* **pbar:** allow specifying another ProgressBar to reuse the Progress widget ([513323f](https://github.com/jungomi/progrich/commit/513323fdc272bd2f367349c5e915977fe9a78570))
* **pbar:** automatically use the default progress manager ([e4b7952](https://github.com/jungomi/progrich/commit/e4b795205527f6c3e147101fdf31a3513e250645))
* **pbar:** provide iter method that wraps a pbar around an iterable ([fd11096](https://github.com/jungomi/progrich/commit/fd11096201c88e89b7f0b0255b28f91ed0bc2897))
* **pbar:** provide update method to change the text of the pbar ([cedeb2c](https://github.com/jungomi/progrich/commit/cedeb2cc81f3355e37c5b503b1213b2594e0e7d8))
* **spinner:** finish spinner with success/failure and persist message ([de5273f](https://github.com/jungomi/progrich/commit/de5273f475b0fb54e815ef5ce6272a723d2085da))
* **spinner:** implement a spinner ([6df5411](https://github.com/jungomi/progrich/commit/6df54116ee3f390fcfb96eaa5f5b6b619393e2f8))


### Bug Fixes

* **manager:** remove duplicate renders when re-enabling the manager ([298ef24](https://github.com/jungomi/progrich/commit/298ef24d8185cbdd869632ed2d0f8d22660c2eb2))
* **pbar:** handle start/stop without context manager ([6737bdc](https://github.com/jungomi/progrich/commit/6737bdc6e7e312b6cdbd075b8cb0c0057db42a76))
* perform specific clean up to avoid errors ([2a0217e](https://github.com/jungomi/progrich/commit/2a0217edb3f811d541b106d74f4f736421583e60))
* resolve formatting in columns ([28e44ab](https://github.com/jungomi/progrich/commit/28e44ab80debc3756a84f1a85e50d6ad9e51b34c))


### Documentation

* create a README ([41b8d40](https://github.com/jungomi/progrich/commit/41b8d40189bfdd680326966a929427114430ba29))
* write doc strings for public classes ([c1bf6d4](https://github.com/jungomi/progrich/commit/c1bf6d4b8214802b1457b76fab345ba426162521))


### Code Refactoring

* rename project to progrich ([49b2bc5](https://github.com/jungomi/progrich/commit/49b2bc5bb89ad1ebe8efd7176c97860806b7adad))
