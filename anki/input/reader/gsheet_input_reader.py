from anki.input.input_data import InputData, InputDataRecord
from anki.input.reader.input_reader import InputReader
from compose.deck_specification import DeckSpecification
import pandas as pd


class GSheetInputReader(InputReader):

    def __int__(self, spec: DeckSpecification):
        super(spec)

    def read_input(self):
        data = InputData()
        df: pd.DataFrame = _merge_sheets(self._spec.input_config.file_path, [sheet_name for sheet_name in self._spec.input_config.sheets])
        data.records = [record for record in self.__iter_records(df)]

        return data

    def __iter_records(self, df: pd.DataFrame):
        for _, row in df.iterrows():
            record: InputDataRecord = self._create_record()
            for field in record.fields:
                field.field_value = row[field.field_name]

            yield record


def _merge_sheets(url: str, sheet_names: list[str]):
    df = None
    for sheet_name in sheet_names:
        df = _sheet_to_df(url, sheet_name) if df is None else df.append(_sheet_to_df(url, sheet_name),
                                                                       ignore_index=True)
    return df


def _sheet_to_df(url: str, sheet_name: str):
    return pd.read_excel(url, sheet_name, index_col="#")
