const HeroSection = () => {
  return (
    <section className="bg-[linear-gradient(180deg,#000_0%,#8F918C_100%)] mt-10 p-10 rounded-[28px]">
      <div className="flex flex-col gap-10">
        <div className="flex justify-between items-center gap-10 max-md:flex-col max-md:items-start">
          <div className="flex flex-col gap-5">
            <h1 className="text-[#D9D9D9] font-normal text-5xl">
              <span className="text-5xl">The </span>
              <span className="text-[#9F91E9] text-5xl">fast lane </span>
              <span>for invoice-to-despatch conversion.</span>
            </h1>
            <p className="text-white text-xl">
              Say goodbye to manual processing—hello efficiency! Optimized for
              accuracy, built for speed.
            </p>
            <div className="text-[#9F91E9] text-[35px] bg-[#2A2B2A] w-fit px-[30px] py-[15px] rounded-full">
              One click, one boost, total transformation.
            </div>
          </div>
          <div>
            <svg
              width="496"
              height="551"
              viewBox="0 0 496 551"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className="w-[488px] h-[543px] max-lg:w-full"
            >
              <g filter="url(#filter0_d_6030_274)">
                <path
                  d="M367 176C367 270.234 287.071 347 188 347C88.9292 347 9 270.234 9 176C9 81.7664 88.9292 5 188 5C287.071 5 367 81.7664 367 176Z"
                  stroke="#F6F4F4"
                  strokeWidth="10"
                  shapeRendering="crispEdges"
                ></path>
              </g>
              <g filter="url(#filter1_d_6030_274)">
                <path
                  d="M487 367C487 461.234 407.071 538 308 538C208.929 538 129 461.234 129 367C129 272.766 208.929 196 308 196C407.071 196 487 272.766 487 367Z"
                  stroke="#F6F4F4"
                  strokeWidth="10"
                  shapeRendering="crispEdges"
                ></path>
              </g>
              <defs>
                <filter
                  id="filter0_d_6030_274"
                  x="0"
                  y="0"
                  width="376"
                  height="360"
                  filterUnits="userSpaceOnUse"
                  colorInterpolationFilters="sRGB"
                >
                  <feFlood
                    floodOpacity="0"
                    result="BackgroundImageFix"
                  ></feFlood>
                  <feColorMatrix
                    in="SourceAlpha"
                    type="matrix"
                    values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
                    result="hardAlpha"
                  ></feColorMatrix>
                  <feOffset dy="4"></feOffset>
                  <feGaussianBlur stdDeviation="2"></feGaussianBlur>
                  <feComposite in2="hardAlpha" operator="out"></feComposite>
                  <feColorMatrix
                    type="matrix"
                    values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.25 0"
                  ></feColorMatrix>
                  <feBlend
                    mode="normal"
                    in2="BackgroundImageFix"
                    result="effect1_dropShadow_6030_274"
                  ></feBlend>
                  <feBlend
                    mode="normal"
                    in="SourceGraphic"
                    in2="effect1_dropShadow_6030_274"
                    result="shape"
                  ></feBlend>
                </filter>
                <filter
                  id="filter1_d_6030_274"
                  x="120"
                  y="191"
                  width="376"
                  height="360"
                  filterUnits="userSpaceOnUse"
                  colorInterpolationFilters="sRGB"
                >
                  <feFlood
                    floodOpacity="0"
                    result="BackgroundImageFix"
                  ></feFlood>
                  <feColorMatrix
                    in="SourceAlpha"
                    type="matrix"
                    values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
                    result="hardAlpha"
                  ></feColorMatrix>
                  <feOffset dy="4"></feOffset>
                  <feGaussianBlur stdDeviation="2"></feGaussianBlur>
                  <feComposite in2="hardAlpha" operator="out"></feComposite>
                  <feColorMatrix
                    type="matrix"
                    values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.25 0"
                  ></feColorMatrix>
                  <feBlend
                    mode="normal"
                    in2="BackgroundImageFix"
                    result="effect1_dropShadow_6030_274"
                  ></feBlend>
                  <feBlend
                    mode="normal"
                    in="SourceGraphic"
                    in2="effect1_dropShadow_6030_274"
                    result="shape"
                  ></feBlend>
                </filter>
              </defs>
            </svg>
          </div>
        </div>
      </div>
    </section>
  );
};
export default HeroSection;
