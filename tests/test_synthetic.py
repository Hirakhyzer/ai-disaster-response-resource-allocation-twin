from disastertwin.synthetic import SyntheticDisasterConfig, generate_synthetic_disaster_data


def test_synthetic_generator_shapes():
    data = generate_synthetic_disaster_data(SyntheticDisasterConfig(zones=8, facilities=5, seed=4))
    assert len(data["zones"]) == 8
    assert len(data["facilities"]) == 5
    assert {"population", "exposure_index", "social_vulnerability_index"}.issubset(data["zones"].columns)
    assert data["zones"]["synthetic_data_notice"].str.contains("fictional").all()
    assert len(data["supplies"]) >= 5 * 6
    assert len(data["roads"]) >= 12
