from importer import parse_amount, parse_csv


def test_parse_common_rupee_formats():
    assert parse_amount("1000") == 1000
    assert parse_amount("1,000") == 1000
    assert parse_amount("₹1,000") == 1000
    assert parse_amount("₹ 1,000") == 1000
    assert parse_amount("Rs. 1000") == 1000
    assert parse_amount("Rs 1,000") == 1000
    assert parse_amount("INR 1000") == 1000
    assert parse_amount("-500") is None
    assert parse_amount("abc") is None


def test_importer_merges_names_and_removes_exact_duplicates():
    csv_text = """name,amount,note
Ayushi Gupta,1000,share
ayushi gupta,1000,share
Aman Singh,500,first
Aman Sing,250,second
"""
    report = parse_csv(csv_text, ["Ayushi Gupta"])

    assert report["rows_found"] == 4
    assert report["imported"] == 3
    assert report["duplicates"] == 1
    assert report["merged"] >= 1
    assert report["rejected"] == 0
    assert report["import_rows"][0]["name"] == "Ayushi Gupta"
    assert any(x["canonical"] == "Aman Singh" for x in report["merged_detail"])


def test_importer_rejects_invalid_rows():
    csv_text = """name,amount,note
,1000,missing name
Karan,abc,bad amount
Priya,-500,negative
"""
    report = parse_csv(csv_text)
    assert report["rows_found"] == 3
    assert report["imported"] == 0
    assert report["rejected"] == 3


def test_same_person_can_make_two_legitimate_payments():
    csv_text = """name,amount,note
Rahul Meena,500,first
Rahul Meena,500,second
"""
    report = parse_csv(csv_text)
    assert report["imported"] == 2
    assert report["duplicates"] == 0
