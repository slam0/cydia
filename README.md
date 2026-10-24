# Repozytorium Cydii (nazar0vsky)

Jedno repozytorium Cydii na wszystkie projekty. Strona: `https://slam0.github.io/cydia/` (Settings → Pages → Source: GitHub Actions).

## Jak to działa

* `projekty.txt` – lista repozytoriów (`wlasciciel/nazwa`), po jednym w linii.
* Workflow **Repozytorium Cydii** (`.github/workflows/repo.yml`) z każdego z nich pobiera pliki `.deb` z wydania
  (Release) o tagu **`najnowsza`**, składa repozytorium APT (`Packages`, `Packages.bz2`, `Release`) i publikuje na GitHub Pages.
* Odświeża się samo codziennie o ~4:17 UTC, po każdej zmianie w tym repozytorium i na żądanie
  (Actions → Repozytorium Cydii → Run workflow).

## Nowy projekt

1. W jego workflow budującym publikuj `.deb` jako wydanie o tagu `najnowsza` (patrz `build.yml` w projekcie Rozklad).
2. Dopisz `slam0/nazwa-projektu` do `projekty.txt`.
3. W pliku `control` paczki warto dać `Icon:` (adres obrazka) i `Depiction:` (adres strony projektu), pokażą się w Cydii i na stronie.

Dodawanie w Cydii: Manage → Sources → Edit → Add → `https://slam0.github.io/cydia/`.

## Test lokalny

`python3 -m unittest discover -s tools/tests -p 'test_build_repo.py'` (wymaga `dpkg-deb`).
