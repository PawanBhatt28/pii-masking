from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
recognizers = analyzer.get_recognizers()

print(f"Total Recognizers: {len(recognizers)}")
for r in recognizers:
    print(f"- {r.name} (Entities: {r.supported_entities})")
