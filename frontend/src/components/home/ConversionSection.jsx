import ConversionForm from "@/components/ui/ConversionForm";
const ConversionSection = () => {
  return (
    <section className="mt-20">
      <div className="flex flex-col items-center gap-10">
        <h2 className="text-[#D9D9D9] text-5xl">Try It Now</h2>
        <div className="w-[298px] h-px bg-[#A193EE]" />
        <ConversionForm />
      </div>
    </section>
  );
};
export default ConversionSection;
