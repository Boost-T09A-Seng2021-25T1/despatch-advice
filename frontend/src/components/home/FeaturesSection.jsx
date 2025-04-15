import FeatureCard from "./FeatureCard";
const FeaturesSection = () => {
  const features = [
    {
      id: 1,
      imageUrl:
        "https://cdn.builder.io/api/v1/image/assets/TEMP/f8813986dc50d4a43ae82d4925510c670bdf43fc",
      title: "Generate Despatch Advice",
      description:
        "Speed through the process of converting you XML Invoice Document to a Despatch Order Advice",
    },
    {
      id: 2,
      imageUrl:
        "https://cdn.builder.io/api/v1/image/assets/TEMP/457286d6bc01d1fd8ab60a5a6c69ad4867fdfc16",
      title: "XML to PDF Converter",
      description:
        "Boost your understanding of XML documents by converting them to PDF",
    },
  ];
  return (
    <section className="mt-20">
      <div className="flex flex-col items-center gap-10">
        <h2 className="text-[#D9D9D9] text-6xl">Features</h2>
        <div className="w-[298px] h-px bg-[#A193EE]" />
        <div className="grid grid-cols-2 gap-10 w-full max-md:grid-cols-1">
          {features.map((feature) => (
            <FeatureCard
              key={feature.id}
              imageUrl={feature.imageUrl}
              title={feature.title}
              description={feature.description}
            />
          ))}
        </div>
      </div>
    </section>
  );
};
export default FeaturesSection;
