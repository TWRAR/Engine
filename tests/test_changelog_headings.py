from src.gui import theme


def test_sort_changelog_sections_handles_date_version_headings():
    md = (
        "## v26.10.23-1\n\n### Changed\n- b\n\n### Added\n- a\n\n"
        "## v26.10.23\n\n### Fixed\n- f\n\n### Security\n- s\n\n### Removed\n- r\n"
    )
    out = theme.sort_changelog_sections(md)
    assert out.index("## v26.10.23-1") < out.index("### Added") < out.index("### Changed")
    assert out.index("## v26.10.23\n") < out.index("### Fixed") < out.index("### Removed") < out.index("### Security")
