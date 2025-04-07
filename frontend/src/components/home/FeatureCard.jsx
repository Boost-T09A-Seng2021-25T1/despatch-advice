const FeatureCard = ({ imageUrl, title, description }) => {
  return (
    <div className="bg-[#2B2A2A] flex flex-col items-center gap-5 p-10 rounded-[28px] border-[3px] border-[#A193EE]">
      <img
        src={imageUrl}
        alt={title}
        className="w-[242px] h-[238px] rounded-full shadow-[0px_4px_4px_rgba(0,_0,_0,_0.25)]"
      />
      <h3 className="text-[#D9D9D9] text-center font-normal text-3xl">
        {title}
      </h3>
      <p className="text-white text-[0px_4px_4px_rgba(0,0,0,0)] text-center">
        {description}
      </p>
    </div>
  );
};

export default FeatureCard;
