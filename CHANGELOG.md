# Changelog

## [v1.5.4](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.5.4) - 2022-08-08

### Changed

- Fix bug in report file exports caused by lack of date search type param

## [v1.5.3](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.5.3) - 2022-07-27

### Changed

- Fix bug in equipment verification where second entry was ignored

## [v1.5.2](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.5.2) - 2022-07-14

### Added

- Implement user-defined date search type (inclusive/exclusive)

### Changed

- Fix bug in DB view report_cooperator_results entry_date field caused by unnecessary type coercion
- Change Balance Verifications to Equipment Verifications

## [v1.5.1](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.5.1) - 2022-06-15

### Fixed

- Fix bug in BathUpload Result constructor that put the constituent value in the analysis field
- Fix BatchUpload bug caused by omitted Analysis field
- Fix datetime-date coercion error in models by using date.today instead of datetime.now
- Include analysis field in BatchUpload mercury service agent loadResult function

## [v1.5.0](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.5.0) - 2022-06-13

### Added

- Add Isotope Uploader Feature
- Add Analysis query parameter to Results endpoint and allow querying of Analysis and Constituent by either ID or name in Results endpoint

## [v1.4.4](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.4.4) - 2022-02-04

### Fixed

- Return a validation warning for SPM batch upload when required tare weight value is not found

## [v1.4.3](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.4.3) - 2022-01-20

### Fixed

- Fix bug in multipage CSV download query caused by analysis value being an empty string

## [v1.4.2](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.4.2) - 2022-01-14

### Added

- Include new analysis/constituent fields from bottle search in the CSV Export function

## [v1.4.1](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.4.1) - 2021-12-20

### Fixed

- Ensure local time is used to populate Add Balance Verification form

## [v1.4.0](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.4.0) - 2021-12-17

### Added

- Add Balance Verification Feature
- Add Analysis/Constituent filter to work with Bottle filter on Sample and Result Search pages

## [v1.3.0](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.3.0) - 2021-08-11

### Added

- Implement Result percent_matching field in Result model: updates to model, serializer, result search page, cooperator report page, and batch upload app, and include migrations in repo
- Include database views in repo (essential to reports part of app)

## [v1.2.6](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.2.6) - 2021-06-01

### Fixed

- Ensure result calculations that require filtered volume return -900 if filtered volume is null, rather than passing through the raw value

## [v1.2.5](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.2.5) - 2020-04-24

### Fixed

- Ensure result calculations that require filtered volume return -999 if filtered volume is null, rather than passing through the raw value

## [v1.2.4](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.2.4) - 2021-11-14

### Changed

- Improve error message in Sample Login unique bottle validation

## [v1.2.3](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.2.3) - 2021-10-29

### Changed

- Change handsontable formatting of depth to four decimal places

## [v1.2.2](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.2.2) - 2019-10-29

### Fixed

- Prevent null numerator error in batch upload of SPM data by returning -999 value when volume_filtered is null

## [v1.2.1](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.2.1) - 2019-09-05

### Fixed

- Fix bug caused by DateField model field defined as DateTimeField in serializer

## [v1.2.0](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.2) - 2019-08-20

### Added

- Add SPM method calculations
- Implement multi-bottle search with preserved search order
- Implement initial API documentation

### Changed  

- Move tare_weight from bottleprefix to bottle
- Update 3rd party libraries

## [v1.1.0](https://github.com/USGS-WiM/merlin_django/releases/tag/v1.1) - 2018-01-29

### Added

- Add new query params

### Changed  

- Upgrade 3rd party libraries
